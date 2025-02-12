import logging, json, shutil, os, io
from pathlib import Path
from flask import request, jsonify

from git import Repo 
import pytest
import pylint.reporters.text as lint_report
import pylint.lint as lint
from contextlib import redirect_stdout, redirect_stderr

import testinfo, notifier, history

def clone_project_upon_push_and_test(payload):
    branch_name = '/'.join((payload["ref"]).split('/')[2:])
    logging.info(branch_name)
    repo_url = payload["repository"]["html_url"]
    
    logging.info("Before commit: "+payload["before"])
    logging.info("Most recent commit: "+payload["after"])

    logging.info("Repository url: "+repo_url)
    clone_dir = "./testingdir"
    if Path(clone_dir).is_dir():
        logging.info(f"Cloning directory {clone_dir} already exists, deleting...")
        shutil.rmtree(clone_dir)
        
    repo = Repo.clone_from(repo_url, clone_dir, branch=branch_name)
    return repo
  
def handle_push_event(payload, token):
    """Handles push events from GitHub webhook by triggering compilation, testing, and notification."""

    # Test the project and gather results
    repo = clone_project_upon_push_and_test(payload)
    test_results = tests_and_compiles_on_push(payload, repo)
    history.write_to_history(test_results)
    for test_info in test_results:
        try:
            notifier.send_commit_status(repo=payload['repository']['full_name'],
                           commit_sha=test_info.commit_id,
                           test_data=test_info,
                           token=token)
        except Exception as e:
            logging.error(f"Error processing push event: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
        
    return jsonify({
        "message": "Push event processed."
    }), 200

def clone_project_upon_pull(payload):
    branch_name = payload["pull_request"]["head"]["ref"]
    logging.info(branch_name)
    repo_url = payload["pull_request"]["head"]["repo"]["html_url"]
    logging.info(repo_url)
    clone_dir = "./testingdir"
    if Path(clone_dir).is_dir():
        logging.info(f"Cloning directory {clone_dir} already exists, deleting...")
        shutil.rmtree(clone_dir)
        
    repo = Repo.clone_from(repo_url, clone_dir, branch=branch_name, single_branch=True)
    return repo
  
def handle_pull_request_event(payload):
    """Handles pull request events from GitHub webhook by running tests and notifying results."""

    theRepo = clone_project_upon_pull(payload)

    try:
        
        return jsonify({
            "message": "Pull request event processed.",
            "test_success": "fail",
            "test_message": "not implemented"
        }), 200
        
    except Exception as e:
        logging.error(f"Error processing pull request event: {str(e)}")
        return jsonify({"error": str(e)}), 500


def check_syntax(dir):
    """Runs pylint syntax test for module in the given directory. Returns 
    boolean pass status and string of pylint result."""

    pylint_output = io.StringIO()
    reporter = lint_report.TextReporter(pylint_output)
    lint.Run(["--disable=R,C,W", "-sn" , dir], reporter=reporter, exit=False)
    pylint_res = pylint_output.getvalue()
    
    lint.pylinter.MANAGER.clear_cache() # Clear cache

    # Formatting
    pylint_res = '\n'.join(pylint_res.split('\n')[1::2])

    if len(pylint_res) == 0:
        pylint_pass = True
        pylint_res = "Pylint syntax test passed succesfully."
    else:
        pylint_pass = False 

    return pylint_pass,pylint_res

def run_tests(test_dir): 
    """
    Runs test suite located in the given directory. Returns boolean 
    pass status and string of pytest report.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    test_dir = os.path.abspath(test_dir)  # Convert to absolute path
    logging.info(f"Testing tests in dir {test_dir}")
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        retcode = pytest.main([test_dir])
    pytest_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()

    if retcode == 0:
        pytest_pass = True
    else:
        pytest_pass = False

    return pytest_pass,"Standard output: "+ pytest_output + "\n" + "Standard error: " + stderr_output


# Placeholder for running tests
def tests_and_compiles_on_push(payload, repo):
    """Creates branch for each commit included in payload, runs compilation and testing for each. Returns
    array of testInfo objects containing the id and test results for each commit."""
    logging.info("Running tests... ")
    
    commits_list = [commit["id"] for commit in payload["commits"]]
    
    test_results = []

    for commit_id in commits_list:
        if not (len(commits_list) == 1):
            repo.git.checkout(commit_id)

        repo.git.checkout(commit_id)

        logging.info(f"\nCompiling Commit: {commit_id}")
        pylint_pass,pylint_output = check_syntax("./testingdir/src")
        logging.info("linter pass: "+str(pylint_pass))

        logging.info(f"\nTesting Commit: {commit_id}")
        pytest_pass,pytest_output = run_tests("./testingdir/tests")        
        logging.info("pytest pass: "+str(pytest_pass))
         
        test_results.append(testinfo.testInfo(
                                            commit_id=commit_id,
                                            passed_pylint=pylint_pass,
                                            passed_test=pytest_pass,
                                            pylint_output=pylint_output,
                                            pytest_output=pytest_output
                                            )
                            )

    shutil.rmtree("./testingdir")
        
    return test_results
