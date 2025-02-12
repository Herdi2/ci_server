import csv

def write_to_history(test_results):
    """Writes each testInfo object to CSV file"""
    formatted_output = []
    titles = ["SHA", "Pylint", "Pytest", "Pylint Output", "Pytest Output"]
    with open("history.csv", mode="a") as f:
        writer = csv.writer(f)
        for test_info in test_results:
            writer.writerow(test_info.to_hist())