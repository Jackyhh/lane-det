import paddle
import paddle.nn as nn


class DownsamplerBlock(nn.Layer):
    def __init__(self, ninput, noutput):
        super().__init__()
        self.conv = nn.Conv2D(ninput, noutput - ninput, (3, 3),
                                         stride=2, padding=1, bias_attr=True)
        # self.pool = nn.MaxPool2D(2, pool_type="max", pool_stride=2)
        self.pool = nn.MaxPool2D(2, stride=2)
        self.bn = nn.BatchNorm(noutput, epsilon=1e-3)

    def forward(self, input):
        output = paddle.concat([self.conv(input), self.pool(input)], axis=1)
        output = self.bn(output)
        # return nn.relu(output)
        return paddle.nn.functional.relu(output)


class non_bottleneck_1d(nn.Layer):
    def __init__(self, chann, dropprob, dilated):
        super().__init__()
        self.conv3x1_1 = nn.Conv2D(chann, chann, (3, 1), stride=1, padding=(1, 0), bias_attr=True)
        self.conv1x3_1 = nn.Conv2D(chann, chann, (1, 3), stride=1, padding=(0, 1), bias_attr=True)
        self.bn1 = nn.BatchNorm(chann, epsilon=1e-03)
        self.conv3x1_2 = nn.Conv2D(chann, chann, (3, 1), stride=1, padding=(1 * dilated, 0), bias_attr=True,
                                              dilation=(dilated, 1))
        self.conv1x3_2 = nn.Conv2D(chann, chann, (1, 3), stride=1, padding=(0, 1 * dilated), bias_attr=True,
                                              dilation=(1, dilated))
        self.bn2 = nn.BatchNorm(chann, epsilon=1e-03)
        self.dropout = nn.Dropout(dropprob)
        self.p = dropprob

    def forward(self, input):
        output = self.conv3x1_1(input)
        output = paddle.nn.functional.relu(output)
        output = self.conv1x3_1(output)
        output = self.bn1(output)
        output = paddle.nn.functional.relu(output)

        output = self.conv3x1_2(output)
        output = paddle.nn.functional.relu(output)
        output = self.conv1x3_2(output)
        output = self.bn2(output)

        if self.p != 0:
            output = self.dropout(output)

        return paddle.nn.functional.relu(output + input)  # +input = identity (residual connection)


class Encoder(nn.Layer):
    def __init__(self, num_classes):
        super().__init__()
        self.initial_block = DownsamplerBlock(3, 16)

        self.layers = nn.LayerList()

        self.layers.append(DownsamplerBlock(16, 64))

        for x in range(0, 5):  # 5 times
            self.layers.append(non_bottleneck_1d(64, 0.1, 1))

        self.layers.append(DownsamplerBlock(64, 128))

        for x in range(0, 2):  # 2 times
            self.layers.append(non_bottleneck_1d(128, 0.1, 2))
            self.layers.append(non_bottleneck_1d(128, 0.1, 4))
            self.layers.append(non_bottleneck_1d(128, 0.1, 8))
            self.layers.append(non_bottleneck_1d(128, 0.1, 16))

        # only for encoder mode:
        self.output_conv = nn.Conv2D(128, num_classes, 1, stride=1, padding=0, bias_attr=True)

    def forward(self, input, predict=False):
        output = self.initial_block(input)

        for layer in self.layers:
            output = layer(output)

        if predict:
            output = self.output_conv(output)

        return output


class UpsamplerBlock(nn.Layer):
    def __init__(self, ninput, noutput, output_size=[16, 16]):
        super().__init__()
        self.conv = paddle.nn.Conv2DTranspose(ninput, noutput, 3, 
                                                      stride=2, padding=1, bias_attr=True)
        self.bn = nn.BatchNorm(noutput, epsilon=1e-3)

    def forward(self, input):
        output = self.conv(input)
        output = self.bn(output)
        return paddle.nn.functional.relu(output)


class Decoder(nn.Layer):
    def __init__(self, num_classes, raw_size=[384, 1024]):
        super().__init__()

        self.layers = nn.LayerList()

        self.layers.append(UpsamplerBlock(128, 64, output_size=[raw_size[0] // 4, raw_size[1] // 4]))
        self.layers.append(non_bottleneck_1d(64, 0, 1))
        self.layers.append(non_bottleneck_1d(64, 0, 1))

        self.layers.append(UpsamplerBlock(64, 16, output_size=[raw_size[0] // 2, raw_size[1] // 2]))
        self.layers.append(non_bottleneck_1d(16, 0, 1))
        self.layers.append(non_bottleneck_1d(16, 0, 1))

        self.output_conv = paddle.nn.Conv2DTranspose(16, num_classes, 2, stride=2,
                                                        #  output_size=[raw_size[0], raw_size[1]],
                                                         padding=0, bias_attr=True)

    def forward(self, input):
        output = input

        for layer in self.layers:
            output = layer(output)

        output = self.output_conv(output)

        return output


class ERFNet(nn.Layer):
    def __init__(self, num_classes, raw_size=[384, 1024]):
        super().__init__()
        self.encoder = Encoder(num_classes)
        self.decoder = Decoder(num_classes, raw_size=raw_size)
        self.input_mean = [103.939, 116.779, 123.68]
        self.input_std = [1, 1, 1]

    def forward(self, input):
        output = self.encoder(input)
        return self.decoder.forward(output)
