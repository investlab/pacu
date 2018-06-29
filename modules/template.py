#!/usr/bin/env python3
import boto3, argparse, os, sys
from botocore.exceptions import ClientError
from functools import partial

from pacu import util

# When writing a module, feel free to remove any comments, placeholders, or anything else that doesn't relate to your module

module_info = {
    # Name of the module (should be the same as the filename)
    'name': 'template',

    # Name and any other notes about the author
    'author': 'You of your company',

    # One liner description of the module functionality. This shows up when a user searches for modules.
    'one_liner': 'Does this thing.',

    # Full description about what the module does and how it works
    'description': 'This module does this thing by using xyz and outputs info to abc. Here is a note also.',

    # A list of AWS services that the module utilizes during its execution
    'services': ['EC2'],

    # For prerequisite modules, try and see if any existing modules return the data that is required for your module before writing that code yourself, that way, session data can stay separated and modular.
    'prerequisite_modules': [],

    # External resources that the module depends on. Valid options are either a GitHub URL (must end in .git) or single file URL.
    'external_dependencies': [],

    # Module arguments to autocomplete when the user hits tab
    'arguments_to_autocomplete': [],
}

parser = argparse.ArgumentParser(add_help=False, description=module_info['description'])

# Just placeholders for arguments, delete/change as needed
# Arguments that accept multiple options (such as --usernames) should be comma-separated (such as --usernames bill,mike,tom)
# Arguments that are region-specific (such as --instance-ids) should use an @ symbol to separate the data and its region (such as --instance-ids 123@us-west-1,54252@us-east-1,9999@ap-south-1
# Make sure to add arguments to module_config['arguments_to_autocomplete']
parser.add_argument('', help='')
parser.add_argument('', required=False, default=None, help='')

# For when "help module_name" is called, don't modify this
def help():
    return [module_info, parser.format_help()]

# Main is the first function that is called when this module is executed
def main(args, proxy_settings, database):
    session = util.get_active_session(database)

    ###### Don't modify these. They can be removed if you are not using the function.
    args = parser.parse_args(args)
    print = partial(util.print, session_name=session.name, database=database)
    input = partial(util.input, session_name=session.name, database=database)
    key_info = partial(util.key_info, database=database)
    fetch_data = partial(util.fetch_data, database=database)
    get_regions = partial(util.get_regions, database=database)
    install_dependencies = partial(util.install_dependencies, database=database)
    ######

    # Use the print and input functions as you normally would. They have been modified to log the data to a history file as well as print it to the screen

    # Fetch information for the currently active set of keys, this returns a dictionary containing information about the AWS key using the session's current key_alias, which includes info like User Name, User Arn, User Id, Account Id, the permissions collected so far for the user, the groups they are a part of, access key id, secret access key, session token, key alias, and a note
    user = key_info()

    # fetch_data is used when there is a prerequisite module to the current module. The example below shows how to fetch all EC2 security group data to use in this module.
    if fetch_data(['EC2', 'SecurityGroups'], 'enum_ec2_sec_groups', '') is False: # This will be false if the user declines to run the pre-requisite module or it fails. Depending on the module, you may still want to continue execution, so building the check is on you as a developer.
        print('Pre-req module not run successfully. Exiting...')
        return
    sec_groups = session.EC2['SecurityGroups']

    # Attempt to install the required external dependencies, exit this module if the download/install fails
    if not install_dependencies(external_dependencies):
        return

    # IMPORTANT NOTE: It is suggested to always utilize the DryRun parameter for boto3 requests that support it. It will test the permissions of the action without actually executing it.

    # Use the get_regions function to fetch an array of supported regions for the service that you pass into it
    regions = get_regions('EC2')

    for region in regions:
        print('Starting region {}...'.format(region))
        client = boto3.client(
            'aws_service',
            region_name=region,
            aws_access_key_id=session.access_key_id,
            aws_secret_access_key=session.secret_access_key,
            # Even if the session doesn't have a session token,
            # this will work because the value will be None and will be ignored:
            aws_session_token=session.session_token,
            # Proxy boto3's client if currently proxying through an agent:
            config=botocore.config.Config(proxies={'https': 'socks5://127.0.0.1:8001', 'http': 'socks5://127.0.0.1:8001'}) if proxy_settings.target_agent is not None else None
        )

    print('{} completed.'.format(os.path.basename(__file__)))
    return
