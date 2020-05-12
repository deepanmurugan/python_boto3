# How to push RabbitMQ metrics to Cloudwatch

### Make sure you add either AWS Credentials or attach role to EC2 instance.
```
Configure AWS Credentials:
sudo apt install awscli
aws configure
```
```
Configure role and attach to EC2. Below is the permissions required.
"ec2:DescribeTags"
"cloudwatch:GetMetricStatistics",
"cloudwatch:ListMetrics",
"cloudwatch:PutMetricData"
```

### Download cloudwatch plugins on your rabbitmq node
```
cd /tmp
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/certifi-2.5.1.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/elixir-1.8.2.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/ex_aws-2.1.0.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/ex_aws_cloudwatch-2.0.4.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/hackney-1.15.2.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/idna-6.0.0.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/logger-1.8.2.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/metrics-1.0.1.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/mimerl-1.2.0.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/poison-3.1.0.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/rabbitmq_cloudwatch_exporter-0.3.1.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/singleton-1.2.0.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/ssl_verify_fun-1.1.5.ez
wget https://github.com/noxdafox/rabbitmq-cloudwatch-exporter/releases/download/0.3.1/unicode_util_compat-0.4.1.ez
```
### Move the plugins to your rabbitmq plugins directory
```
mv /tmp/*.ez /usr/lib/rabbitmq/lib/rabbitmq_server-3.8.3/plugins
```
### Enable the plugin
```
rabbitmq-plugins enable rabbitmq_cloudwatch_exporter
```
### Verify if the plugin is enabled
```
rabbitmq-plugins list
```
```
You will see something like this [E*] when the plugin is enabled, which means the plugin is explicitly enabled.
[E*] rabbitmq_cloudwatch_exporter      0.3.1
```
### Update rabbitmq config file
```
echo "cloudwatch_exporter.metrics.1 = overview
cloudwatch_exporter.metrics.2 = vhost
cloudwatch_exporter.metrics.3 = node
cloudwatch_exporter.metrics.4 = exchange
cloudwatch_exporter.metrics.5 = queue
cloudwatch_exporter.metrics.6 = connection
cloudwatch_exporter.metrics.7 = channel" >> /etc/rabbitmq/rabbitmq.conf
```
```
If you don't want any of the metrics you can remove it from the config. Ex: If you are not using channel/connection you can remove last 2 lines.
cloudwatch_exporter.aws.region = "us-east-2" => Add this line also to /etc/rabbitmq/rabbitmq.conf if you want to push cloudwatch metrics to a different region other than the default region.
```
### Restart the rabbitmq service to take new config
```
sudo service rabbitmq-server restart
```

You will see the metrics under RabbitMQ namespace in AWS Cloudwatch under your default AWS Region or cloudwatch_exporter.aws.region.
