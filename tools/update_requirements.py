from importlib.metadata import PackageNotFoundError, distribution

# Load the existing requirements.txt file
with open("requirements.txt") as file:
    requirements = file.readlines()

updated_requirements = []

for requirement in requirements:
    package_name = requirement.strip().split("==")[0]
    try:
        # Get the installed version of the package
        version = distribution(package_name).version
        updated_requirements.append(f"{package_name}=={version}")
    except PackageNotFoundError:
        # If the package is not installed, keep the original line
        print(f"Package '{package_name}' is not installed.")
        updated_requirements.append(requirement.strip())

# Write the updated requirements back to the file
with open("requirements.txt", "w") as file:
    file.write("\n".join(updated_requirements))

print("requirements.txt has been updated with the installed package versions.")
