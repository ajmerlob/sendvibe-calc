aws ecr get-login --no-include-email --region us-west-2 > run.sh
sh run.sh
docker build -t sendvibe_calc .
docker tag sendvibe_calc:latest 985724320380.dkr.ecr.us-west-2.amazonaws.com/sendvibe_calc:latest
docker push 985724320380.dkr.ecr.us-west-2.amazonaws.com/sendvibe_calc:latest
