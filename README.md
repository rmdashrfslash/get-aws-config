# get-aws-config

get-aws-config is a tool created to fetch configuration data from certain services (currently secrets manager and s3) to be consumed by a container.  The goal is to make containers that have very little configurations inside of them, and instead by using shared volumes, you can inject the configuration in.