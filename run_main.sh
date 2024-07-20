set -e
python3 main.py \
    --month 7 \
    --day 4 \
    --year 2024 \
    --group_size 1 \
    --url "https://www.recreation.gov/permits/4675309" \
    --config_file "config/config.ini" \
    --check_availability_every 10 \
    --send_status_at "12:53" \