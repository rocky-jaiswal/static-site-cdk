# Static Site with CDK

Python CDK project to deploy a static site to AWS Cloudfront backed by a S3 bucket

## Useful commands

 * `npx cdk ls`          list all stacks in the app
 * `npx cdk synth`       emits the synthesized CloudFormation template
 * `npx cdk diff`        compare deployed stack with current state
 * `npx cdk deploy`      deploy this stack to your default AWS account/region
 * `npx cdk destroy`     destroy stack
 * `npx cdk docs`        open CDK documentation
 * `npx cdk bootstrap`   bootstrap CDK (only 1 time)

Enjoy!

## Note

- First time, check if any old stack is present in CloudFormation and delete it, `the run npx cdk bootstrap` otherwise CDK complains of "bootstrap error" :shrug: