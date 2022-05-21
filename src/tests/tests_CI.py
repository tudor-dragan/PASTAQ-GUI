import test_params as params
import test_files as files

print("CI testing suite for PASTAQ-GUI")

print("Testing parameters...")
params.tests_CI()
print("Ran all parameter tests successfully!")

print("Testing files...")
files.tests_CI()
print("Ran all file tests successfully!")

print("All tests run successfully.")