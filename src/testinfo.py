class testInfo:
    """Create object containing the compilation and test results for a commit message of a given SHA id."""

    def __init__(self,
                 commit_id,
                 passed_pylint,
                 passed_test,
                 pylint_output,
                 pytest_output
                 ):
        self.commit_id = commit_id
        self.passed_pylint = passed_pylint
        self.passed_test = passed_test
        self.pylint_output = pylint_output
        self.pytest_output = pytest_output
        
    def to_hist(self):
        return [self.commit_id, 
                self.passed_pylint, 
                self.passed_test,
                self.pylint_output,
                self.pytest_output]