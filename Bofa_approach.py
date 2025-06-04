import os
import re
import subprocess
import pandas as pd
from datetime import datetime
import zipfile

# Your existing SQL patterns

sql_patterns = [
    r"(?i)\bSELECT\b\s+.*?\bFROM\b\s+.*?;",
    r"(?i)\bINSERT\b\s+INTO\b\s+.*?\bVALUES\b\s*\(.*?\);",
    r"(?i)\bUPDATE\b\s+.*?;",
    r"(?i)\bDELETE\b\s+FROM\b\s+.*?;",
    r"(?i)\bDROP\b\s+.*?;",
    r"(?i)\bCREATE\b\s+.*?;",
    r"(?i)\bALTER\b\s+.*?;",
    r"(?i)\bTRUNCATE\b\s+.*?;",
    r"(?i)\bGRANT\b\s+.*?;",
    r"(?i)\bREVOKE\b\s+.*?;",
    r"(?i)\bMERGE\b\s+.*?;",
   # r"(?i)\bEXECUTE\b\s+.*?;",
   # r"(?i)\bCALL\b\s+.*?;",
    r"(?i)\bDECLARE\b\s+.*?;",
    r"(?i)\bSET\b\s+.*?;",
    r"(?i)\bUSE\b\s+.*?;",
    r"(?i)\bBEGIN\b\s+.*?;",
    r"(?i)\bEND\b\s+.*?;",
    r"(?i)\bIF\b\s+.*?\bTHEN\b\s+.*?;",
    r"(?i)\bELSE\b\s+.*?;",
    r"(?i)\bWITH\b\s+[a-zA-Z0-9_]+\s+AS\s*\(.*?\)",  # Matches CTEs
    r"(?i)\bCOMMIT\b",  # Matches "COMMIT"
    r"(?i)\bROLLBACK\b",  # Matches "ROLLBACK"
    r"(?i)\bPROC\b",  # Matches PROC keyword
    r"(?i)\bIDENTITY\b",  # Matches IDENTITY (commonly used in Sybase)
]

stored_procedures_patterns = [
    r"(?i)\bEXEC\b\s+.*?;",  # Matches EXEC keyword
    r"(?i)\bCALL\b\s+.*?;",  # Matches CALL keyword
    r"(?i)\bPROC\b\s+.*?;",  # Matches PROC keyword
    r"(?i)\bEXECUTE\b\s+.*?;"
]


def extract_zip(jar_path,extracted_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            jar.extractall(extracted_path)
            print(f"Extracted {jar_path} to {extracted_path}")
    except Exception as e:
        print(f"Error extracting {jar_path}: {e}")


def decompile_class_file(class_file_path, output_dir):
    try:
        # Call CFR decompiler
        
        subprocess.run(['C:/Program Files/Eclipse Adoptium/jdk-21.0.6.7-hotspot/bin/java.exe', '-jar', r"C:\Users\10735332\Downloads\cfr-0.152.jar", class_file_path, '--outputdir', output_dir],
        check=True,
        capture_output=True,
        text=True
    )

        print(f"Decompiled {class_file_path} to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error decompiling {class_file_path}: {e}")

def extract_sql_from_file(file_path, sql_patterns, stored_procedures_patterns):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            sql_queries = []
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    start_line = content.count('\n', 0, match.start()) + 1
                    sql_queries.append((file_path, start_line, match.group().strip(), "Native SQL"))
            for pattern in stored_procedures_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    start_line = content.count('\n', 0, match.start()) + 1
                    sql_queries.append((file_path, start_line, match.group().strip(), "Stored Procedure/Function"))
            return sql_queries
    except (IOError, UnicodeDecodeError, PermissionError) as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def search_sql_in_repo(repo_path, sql_patterns):
    all_queries = []
    try:
        if not os.path.exists(repo_path):
            print(f"Repository path not found: {repo_path}")
            return []

        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(".class"):
                    decompile_class_file(file_path, "samples/decompiled_files")
                    continue
                if file_path.endswith(".jar"):
                    extract_zip(file_path, "samples/jar_files")
                    continue
                sql_queries = extract_sql_from_file(file_path, sql_patterns, stored_procedures_patterns)
                if sql_queries:
                    all_queries.extend(sql_queries)
        print(f"Found {len(all_queries)} SQL queries in the repository.")
        return all_queries
    except (IOError, PermissionError) as e:
        print(f"Error processing repository: {e}")

def save_to_excel(data, output_file):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        data_with_date = [row + (current_date,) for row in data]
        df = pd.DataFrame(data_with_date, columns=["File Path", "Line Number", "SQL Query", "Category", "Date"])
        df.sort_values(by=["File Path", "Line Number"], inplace=True)
        #print(df)
        if os.path.exists(output_file):
            df_existing = pd.read_excel(output_file, engine='openpyxl')
            df_combined = pd.concat([df_existing, df], ignore_index=True)
        else:
            df_combined = df
        df_combined.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel file {output_file}: {e}")

if __name__ == "__main__":
    repo_path = 'samples'
    output_excel_file = 'sql_queries.xlsx'


    sql_queries = search_sql_in_repo(repo_path, sql_patterns)
    if sql_queries:
        save_to_excel(sql_queries, output_excel_file)
