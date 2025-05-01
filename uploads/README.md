Run on EC2 using nohup

nohup python3 app.py > output.log 2>&1 &

nohup litellm --model gpt-3.5-turbo --host 0.0.0.0 --port 4000 > proxy.log 2>&1 &
