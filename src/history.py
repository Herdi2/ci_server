import csv

def write_to_history(test_results):
    """Writes each testInfo object to CSV file"""
    titles = ["commit_id",
             "passed_pylint",
             "passed_test",
             "pylint_output",
             "pytest_output"]
    with open("history.csv", mode="a") as f:
        writer = csv.DictWriter(f, titles)
        writer.writeheader()
        for test_info in test_results:
            writer.writerow(test_info.to_hist())
            
def read_history():
    with open("history.csv", mode="r") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    return data