import pandas as pd
from pathlib import Path
import logging

# Logging Configuration

logging.basicConfig(
    filename="logs/etl_validation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def load_datasets():

    project_path = Path(__file__).resolve().parent.parent

    source_file = project_path / "input" / "source_orders.csv"
    target_file = project_path / "input" / "target_orders.xlsx"

    try:
        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file not found: {source_file}"
            )

        if not target_file.exists():
            raise FileNotFoundError(
                f"Target file not found: {target_file}"
            )

        source_df = pd.read_csv(source_file)
        target_df = pd.read_excel(target_file)

        print("Datasets loaded successfully!")
        print("Source records:", len(source_df))
        print("Target records:", len(target_df))

        return source_df, target_df, project_path

    except (FileNotFoundError, PermissionError, pd.errors.ParserError) as error:
        print("ERROR loading datasets:", error)
        raise

def validate_input_columns(source_df, target_df):

    required_columns = [
        "order_id",
        "customer_name",
        "city",
        "quantity",
        "unit_price",
        "status",
        "order_total"
    ]

    source_missing = [
        col for col in required_columns
        if col not in source_df.columns
    ]

    target_missing = [
        col for col in required_columns
        if col not in target_df.columns
    ]

    if source_missing or target_missing:

        raise ValueError(
            f"Missing columns in source: {source_missing}\n"
            f"Missing columns in target: {target_missing}"
        )

    print("\nInput column validation: PASSED")

def validate_duplicate_columns(source_df, target_df):

    source_duplicates = source_df.columns[
        source_df.columns.duplicated()
    ].tolist()

    target_duplicates = target_df.columns[
        target_df.columns.duplicated()
    ].tolist()

    if source_duplicates or target_duplicates:
        raise ValueError(
            f"Duplicate columns in source: {source_duplicates}\n"
            f"Duplicate columns in target: {target_duplicates}"
        )

    print("Duplicate column validation: PASSED")

def validate_data_types(source_df, target_df):

    numeric_columns = [
        "order_id",
        "quantity",
        "unit_price",
        "order_total"
    ]

    for column in numeric_columns:

        if not pd.api.types.is_numeric_dtype(source_df[column]):
            raise TypeError(
                f"Source column '{column}' must be numeric"
            )

        if not pd.api.types.is_numeric_dtype(target_df[column]):
            raise TypeError(
                f"Target column '{column}' must be numeric"
            )

    print("Data type validation: PASSED")

def validate_primary_key(source_df, target_df):

    for name, df in [
        ("Source", source_df),
        ("Target", target_df)
    ]:

        null_count = df["order_id"].isnull().sum()

        if null_count > 0:
            raise ValueError(
                f"{name} dataset contains {null_count} NULL order_id values"
            )

    print("Primary key validation: PASSED")


def validate_empty_values(source_df, target_df):

    text_columns = ["customer_name", "city", "status"]

    results = []

    for name, df in [
        ("Source", source_df),
        ("Target", target_df)
    ]:

        for column in text_columns:

            empty_count = int(
                df[column].astype("string").str.strip().eq("").sum()
            )

            results.append({
                "Dataset": name,
                "Column": column,
                "Empty_Count": empty_count,
                "Status": "PASS" if empty_count == 0 else "FAIL"
            })

    result_df = pd.DataFrame(results)

    print("\n===== EMPTY VALUE VALIDATION =====")
    print(result_df.to_string(index=False))

    return result_df


def validate_mandatory_fields(source_df, target_df):

    mandatory_columns = [
        "order_id",
        "customer_name",
        "quantity",
        "unit_price",
        "order_total"
    ]

    results = []

    for name, df in [
        ("Source", source_df),
        ("Target", target_df)
    ]:

        for column in mandatory_columns:

            null_count = int(df[column].isnull().sum())

            results.append({
                "Dataset": name,
                "Column": column,
                "NULL_Count": null_count,
                "Status": "PASS" if null_count == 0 else "FAIL"
            })

    result_df = pd.DataFrame(results)

    print("\n===== MANDATORY FIELD VALIDATION =====")
    print(result_df.to_string(index=False))

    return result_df



# 2. Compare source and target records
def validate_records(source_df, target_df):

    source_ids= set(source_df['order_id'])
    target_ids= set(target_df['order_id'])

     # Records missing in target
    missing_records = source_ids - target_ids
   

# Extra records in target
    extra_records = target_ids - source_ids

    print("\n===== RECORD RECONCILIATION =====")

    print("Missing records in target:", missing_records)
    print("Extra records in target:", extra_records)

    print("Missing record count:", len(missing_records))
    print("Extra record count:", len(extra_records))
    return missing_records, extra_records


# Step 3: Duplicate record detection
def validate_duplicates(source_df, target_df):
    source_duplicates=source_df[source_df['order_id'].duplicated(keep=False)]


    target_duplicates = target_df[
    target_df.duplicated(["order_id"], keep=False)]

    print("\n===== DUPLICATE RECORD CHECK =====")
    print("Source duplicate count:", len(source_duplicates))
    print("Target duplicate count:", len(target_duplicates))
    return source_duplicates, target_duplicates



# Step 4: NULL value validation

def validate_nulls(source_df, target_df):

    source_nulls = source_df.isnull().sum()
    target_nulls = target_df.isnull().sum()

    print("\n===== NULL VALIDATION =====")

    print("\nSource NULL values:")
    print(source_nulls)

    print("\nTarget NULL values:")
    print(target_nulls)

    return source_nulls, target_nulls

# Step 5: Improved column-level validation

def validate_columns(source_df, target_df):

    comparison_columns = [
        "customer_name",
        "city",
        "quantity",
        "unit_price",
        "status",
        "order_total"
    ]

    source_clean = source_df.drop_duplicates(
        subset=["order_id"], keep=False
    )

    target_clean = target_df.drop_duplicates(
        subset=["order_id"], keep=False
    )

    print("\n===== DUPLICATE RECORD EXCLUSION =====")

    print("Source records excluded:",
      len(source_df) - len(source_clean))

    print("Target records excluded:",
      len(target_df) - len(target_clean))

    matched_df = source_clean.merge(
        target_clean,
        on="order_id",
        how="inner",
        suffixes=("_source", "_target")
    )

    mismatch_results = []

    for column in comparison_columns:

        source_col = column + "_source"
        target_col = column + "_target"

        if column in ["quantity", "unit_price", "order_total"]:

            source_values = pd.to_numeric(
                matched_df[source_col], errors="coerce"
            )

            target_values = pd.to_numeric(
                matched_df[target_col], errors="coerce"
            )

            mismatch = ~(
                source_values.eq(target_values)
                | (source_values.isna() & target_values.isna())
            )

        else:

            source_values = matched_df[source_col].fillna("<NULL>").astype(str)
            target_values = matched_df[target_col].fillna("<NULL>").astype(str)

            mismatch = source_values != target_values

        result = matched_df.loc[
            mismatch,
            ["order_id", source_col, target_col]
        ]

        print(f"\n{column} mismatches: {len(result)}")

        mismatch_results.append(result)

    return matched_df, mismatch_results


# Step 6: Business Rule Validation


def validate_business_rules(df, dataset_name):

    expected_total = (
        df["quantity"] * df["unit_price"]
    )

    failures = df[
        df["order_total"] != expected_total
    ].copy()

    failures["expected_total"] = expected_total[
        failures.index
    ]

    print(f"\n===== {dataset_name} BUSINESS RULE VALIDATION =====")
    print("Records checked:", len(df))
    print("Business rule failures:", len(failures))

    return failures


# Step 11.7: Main Function

def main():
    logging.info("===== ETL VALIDATION STARTED =====")
    source_df, target_df, project_path = load_datasets()
    logging.info("Source and target datasets loaded successfully")
    validate_input_columns(source_df, target_df)
    validate_duplicate_columns(source_df, target_df)
    validate_data_types(source_df, target_df)
    validate_primary_key(source_df, target_df)
    empty_results = validate_empty_values(
    source_df, target_df
)
    mandatory_results=validate_mandatory_fields(source_df, target_df)

    missing_records, extra_records = validate_records(
        source_df, target_df
    )

    source_duplicates, target_duplicates = validate_duplicates(
        source_df, target_df
    )

    source_nulls, target_nulls = validate_nulls(
        source_df, target_df
    )

    matched_df, mismatch_results = validate_columns(
        source_df, target_df
    )
    
    

    source_business_rule_failures = validate_business_rules(
    source_df, "Source"
    )

    target_business_rule_failures = validate_business_rules(
    target_df, "Target"
    )

    report_df = generate_validation_report(
        source_df, target_df,
        missing_records, extra_records,
        source_duplicates, target_duplicates,
        source_nulls, target_nulls,
        source_business_rule_failures,
        target_business_rule_failures,
        mandatory_results,
        empty_results
    )
    logging.info("Excel reports generated successfully")
    logging.info("===== ETL VALIDATION COMPLETED =====")

    mismatch_df = collect_mismatch_records(
        missing_records, extra_records,
        target_duplicates, target_df,
        mismatch_results
    )
    logging.info(
    "Total mismatch issues found: %s",
    len(mismatch_df))
    
    

    export_reports(
    report_df,
    mismatch_df,
    project_path,
    source_business_rule_failures,
    target_business_rule_failures
)




# Step 7: Generate Validation Summary

def generate_validation_report(
    source_df, target_df,
    missing_records, extra_records,
    source_duplicates, target_duplicates,
    source_nulls, target_nulls,
    source_business_rule_failures,
    target_business_rule_failures,
    mandatory_results,
    empty_results
):

    validation_results = [
        {
    "Test Case": "Mandatory Field Validation",
    "Records Checked": len(mandatory_results),
    "Failures": int(
        (mandatory_results["Status"] == "FAIL").sum()
    )
    
    },
    {
    "Test Case": "Empty Value Validation",
    "Records Checked": len(empty_results),
    "Failures": int(
        (empty_results["Status"] == "FAIL").sum()
    )
},
        {
            "Test Case": "Row Count",
            "Records Checked": len(source_df),
            "Failures": abs(len(source_df) - len(target_df))
        },
        {
            "Test Case": "Missing Records",
            "Records Checked": len(source_df),
            "Failures": len(missing_records)
        },
        {
            "Test Case": "Extra Records",
            "Records Checked": len(target_df),
            "Failures": len(extra_records)
        },
        {
            "Test Case": "Source Duplicates",
            "Records Checked": len(source_df),
            "Failures": len(source_duplicates)
        },
        {
            "Test Case": "Target Duplicates",
            "Records Checked": len(target_df),
            "Failures": len(target_duplicates)
        },
        {
            "Test Case": "Source NULL Values",
            "Records Checked": len(source_df),
            "Failures": int(source_nulls.sum())
        },
        {
            "Test Case": "Target NULL Values",
            "Records Checked": len(target_df),
            "Failures": int(target_nulls.sum())
        },
        {
    "Test Case": "Source Business Rule",
    "Records Checked": len(source_df),
    "Failures": len(source_business_rule_failures)
},
{
    "Test Case": "Target Business Rule",
    "Records Checked": len(target_df),
    "Failures": len(target_business_rule_failures)
}
    ]

    report_df = pd.DataFrame(validation_results)

    # Ensure all failure counts display as numbers, including zero
    report_df["Failures"] = (
    pd.to_numeric(report_df["Failures"], errors="coerce")
    .fillna(0)
    .astype(int)
    )

    print("\n===== VALIDATION SUMMARY CHECK =====")
    print(report_df.to_string(index=False))

    report_df["Status"] = report_df["Failures"].apply(
        lambda count: "PASS" if count == 0 else "FAIL"
    )

    return report_df

# Step 8: Collect Detailed Mismatch Records

def collect_mismatch_records(
    missing_records, extra_records,
    target_duplicates, target_df,
    mismatch_results
):

    mismatch_records = []

    for order_id in missing_records:
        mismatch_records.append({
            "order_id": order_id,
            "Issue_Type": "Missing Record",
            "Column": "order_id",
            "Source_Value": order_id,
            "Target_Value": None,
            "Issue_Description":
                "Record exists in source but not in target"
        })

    for order_id in extra_records:
        mismatch_records.append({
            "order_id": order_id,
            "Issue_Type": "Extra Record",
            "Column": "order_id",
            "Source_Value": None,
            "Target_Value": order_id,
            "Issue_Description":
                "Record exists in target but not in source"
        })

    for order_id in target_duplicates["order_id"].unique():
        mismatch_records.append({
            "order_id": order_id,
            "Issue_Type": "Duplicate Record",
            "Column": "order_id",
            "Source_Value": None,
            "Target_Value": order_id,
            "Issue_Description":
                "Duplicate order ID found in target dataset"
        })

    for column in target_df.columns:
        null_rows = target_df[target_df[column].isnull()]

        for _, row in null_rows.iterrows():
            mismatch_records.append({
                "order_id": row["order_id"],
                "Issue_Type": "NULL Value",
                "Column": column,
                "Source_Value": None,
                "Target_Value": None,
                "Issue_Description":
                    f"NULL value found in target column: {column}"
            })

    comparison_columns = [
        "customer_name", "city", "quantity",
        "unit_price", "status", "order_total"
    ]

    for column, result in zip(comparison_columns, mismatch_results):

        for _, row in result.iterrows():
            mismatch_records.append({
                "order_id": row["order_id"],
                "Issue_Type": "Column Mismatch",
                "Column": column,
                "Source_Value": row[column + "_source"],
                "Target_Value": row[column + "_target"],
                "Issue_Description":
                    f"Source and target values do not match for {column}"
            })

    return pd.DataFrame(mismatch_records)



def export_reports(
    report_df,
    mismatch_df,
    project_path,
    source_business_rule_failures,
    target_business_rule_failures
):

    output_folder = project_path / "output"
    output_folder.mkdir(exist_ok=True)

    report_file = output_folder / "validation_report.xlsx"
    mismatch_file = output_folder / "mismatch_records.xlsx"

    # Export validation report with multiple sheets
    with pd.ExcelWriter(report_file, engine="openpyxl") as writer:

        report_df.to_excel(
            writer,
            sheet_name="Validation Summary",
            index=False
        )

        source_business_rule_failures.to_excel(
            writer,
            sheet_name="Source Business Rules",
            index=False
        )

        target_business_rule_failures.to_excel(
            writer,
            sheet_name="Target Business Rules",
            index=False
        )

    # Export mismatch records
    mismatch_df.to_excel(mismatch_file, index=False)

    print("\n===== REPORTS GENERATED =====")
    print("Validation report:", report_file)
    print("Mismatch report:", mismatch_file)
    print("Total mismatch issues:", len(mismatch_df))





if __name__ == "__main__":

    try:
        main()

    except FileNotFoundError:
        logging.exception("Required input file not found")

    except PermissionError:
        logging.exception("File permission error occurred")

    except ValueError:
        logging.exception("Input data validation failed")

    except Exception:
        logging.exception("Unexpected error occurred")

    finally:
        logging.info("===== ETL VALIDATION PROCESS ENDED =====")
