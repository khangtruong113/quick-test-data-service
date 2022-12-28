# quick-test-data-service

## Install Python Package
```
pip install -r requirements.txt
```
## Run Test
### Mô tả
- uc: tên uc tương ứng với tên folder được cấu trúc như sau:
```
<uc_name>/
  schema.csv 
  response.json
```
### Full Valid Check
```
python moha_tc_api.py --uc=mock --option=full --group_code=A001 --ma_dv_hc=52 --ky_du_lieu=2021 --date_key=nam
```
### Required Valid Check
```
python moha_tc_api.py --uc=mock --option=required --group_code=A001 --ma_dv_hc=52 --ky_du_lieu=2021 --date_key=nam
```
