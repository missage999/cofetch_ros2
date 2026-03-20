#!/usr/bin/env python3

import sys
import subprocess


def run_test_package(package_name):
    print(f"\n{'='*60}")
    print(f"Testing package: {package_name}")
    print('='*60)

    result = subprocess.run(
        ['python3', '-m', 'pytest', f'test_{package_name}.py', '-v'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def main():
    packages = [
        'cofetch_msgs',
    ]

    results = {}
    for pkg in packages:
        results[pkg] = run_test_package(pkg)

    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)

    for pkg, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  {pkg}: {status}")

    all_passed = all(results.values())
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()