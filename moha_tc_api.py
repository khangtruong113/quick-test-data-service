import argparse

import json
import sys

import pandas as pd
import logging

ENCODING = 'utf-8'
SCHEMA_FILENAME = "schema.csv"
RESPONSE_FILENAME = "response.json"
LOGGING_FILE = "test_case.log"


def read_response(parent_path, filename) -> dict:
    """
    Read Data from Response json file
    """
    more_path = f"{parent_path}/{filename}"
    with open(more_path, encoding=ENCODING) as f:
        logging.info("Reading response file.")
        r = json.load(f)
        f.close()
    return r


def read_schema_csv(parent_path, filename) -> pd.DataFrame:
    more_path = f"{parent_path}/{filename}"
    logging.info(f"Reading schema file {more_path}")
    try:
        csv_reader = pd.read_csv(more_path)
        return csv_reader
    except FileNotFoundError as e:
        logging.error(f"File {more_path} does not exists. {e.errno}")
        sys.exit(1)


def get_header(df: pd.DataFrame) -> str | None:
    """
    Get First Header from schema csv file
    """
    cols = df.columns.to_list()
    if len(cols) == 1:
        return cols[0]
    return None


def get_sec_header(df: pd.DataFrame, f_header: str | None) -> str | None:
    """
    Get Second Header from schema csv file
    """
    if get_header(df) is not None:
        return df.get(f_header)[0]
    return None


def get_field_list(df: pd.DataFrame, f_header: str | None) -> set | None:
    """
    Get Field List from schema csv file
    """
    if get_sec_header(df, f_header) is not None:
        return set(df[f_header].values.tolist()[1:])
    return None


def quick_check_schema_file(f_header: str | None, sec_header: str | None, schema_field_list: set | None) -> bool:
    logging.info("Checking schema file data.")
    if f_header is None:
        logging.error("First header is not valid.")
        sys.exit(1)
    if sec_header is None or sec_header != 'data':
        logging.error("Second header (data) is not valid")
        sys.exit(1)
    if len(schema_field_list) == 0:
        logging.error("Field list is not valid. Number of field is zero")
        sys.exit(1)
    return True


def extract_schema_file(parent_path, filename):
    """
    Read, check and extract schema file
    """
    logging.info(f"[SCHEMA] parent_path={parent_path}|filename={filename}")
    schema_file_df = read_schema_csv(parent_path, filename)
    object_name = get_header(schema_file_df)
    data_field = get_sec_header(schema_file_df, object_name)
    inner = get_field_list(schema_file_df, object_name)
    if quick_check_schema_file(object_name, data_field, inner):
        logging.info("Checking success.")
        logging.info(f"[SCHEMA] object_name={object_name}, fields={inner}")
        return object_name, data_field, inner
    return False


def get_data_object_response(response: dict, obj_schema: str) -> str | None:
    if response.__len__() == 1:
        if response.get(obj_schema) is not None:
            logging.info("object_name values matched.")
            return obj_schema
        logging.info("object_name values not matched.")
        return None
    logging.error("object_name cannot be extracted, response message returns other than 1 object_name.")
    return None


def get_data_name_response(data_res: dict, data_name_schema: str) -> str | None:
    logging.info("Checking data key value.")
    if data_res.get(data_name_schema) is not None:
        logging.info(f"data key values matched. Number records: {data_res.get(data_name_schema).__len__()}")
        return data_name_schema
    logging.info("data key values not matched")
    return None


def is_matched_fields_res(data, field_schema) -> bool:
    logging.info("Checking fields in response.")

    # Check field
    for element in data:
        if set(element.keys()) != field_schema:
            logging.error("[FIELD_CHECK] Field not matched")
            return False
    logging.info("[FIELD_CHECK] Field matched. PASSED")
    return True

def full_valid_check(response_data, object_res_name, data_key_res_name, arguments):
    logging.info("Full Valid Checking.")
    group_code = arguments.group_code
    ma_dv_hc = arguments.ma_dv_hc
    ky_du_lieu = arguments.ky_du_lieu
    date_key = arguments.date_key
    logging.info(f"group_code = [{group_code}], ma_dv_hc = [{ma_dv_hc}], ky_du_lieu = [{ky_du_lieu}], date_key = [{date_key}]")
    for element in response_data[object_res_name][data_key_res_name]:
        if element['group_code'] != group_code:
            logging.error(f"group_code not matched. Expected: [{group_code}], Actual: [{element['group_code']}]")
            return False
        if element['ma_dv_hc'] != ma_dv_hc:
            logging.error(f"ma_dv_hc not matched. Expected: [{ma_dv_hc}], Actual: [{element['ma_dv_hc']}]")
            return False
        if element[date_key] != ky_du_lieu:
            logging.error(f"ky_du_lieu not matched. Expected: [{ky_du_lieu}], Actual: [{element[date_key]}]")
            return False
    logging.info("[FULL_VALID_CHECK] All Matched. PASSED")
    return True

def required_valid_check(response_data, object_res_name, data_key_res_name, arguments):
    logging.info("Required Valid Checking.")
    group_code = arguments.group_code
    logging.info(f"group_code = [{group_code}]")
    for element in response_data[object_res_name][data_key_res_name]:
        if element['group_code'] != group_code:
            logging.error(f"group_code not matched. Expected: [{group_code}], Actual: [{element['group_code']}]")
            return False
    logging.info("[REQUIRED_VALID_CHECK] All Matched. PASSED")
    return True

if __name__ == '__main__':
    # Parser configuration
    parser = argparse.ArgumentParser(
        prog='TC Data Service',
        description='Test Case Data Service',
    )
    parser.add_argument('--uc', required=True, help='Use Case Index')
    parser.add_argument('--option', required=True, help='Option Check: full_param, only_required_param')
    parser.add_argument('--group_code', required=True, help='group_code')
    parser.add_argument('--ma_dv_hc', required=False, help='ma_dv_hc')
    parser.add_argument('--ky_du_lieu', required=False, help='ky_du_lieu')
    parser.add_argument('--date_key', required=False, help='Lay theo nam hoac nhiem_ky')

    # Logging configuration
    logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO, handlers=[
            logging.FileHandler(LOGGING_FILE),
            logging.StreamHandler(sys.stdout)
        ])
    args: argparse.Namespace = parser.parse_args()
    uc = args.uc
    option = args.option
    logging.info("------------TEST-CASE-DATA-SERVICE------------")
    logging.info(f"Input: UC_NAME={uc},CHECK_OPTION={option}")
    accepted_params = ('full', 'required')
    if option not in accepted_params:
        logging.error("Option value is not valid")
        sys.exit(1)
    obj_name, data_name, fields = extract_schema_file(uc, SCHEMA_FILENAME)

    res = read_response(uc, RESPONSE_FILENAME)
    obj_res = get_data_object_response(res, obj_name)
    data_name_res = get_data_name_response(res.get(obj_res), data_name)
    inner_data = res[obj_res][data_name_res]
    is_matched_field = is_matched_fields_res(inner_data, fields)
    logging.info(f"Valid Check option: {option}")
    if option == 'full':
        full_valid_check(res, obj_res, data_name_res, args)
    if option == 'required':
        required_valid_check(res, obj_res, data_name_res, args)
