import subprocess
import time
import csv 
import glob


csvwriter = ""
csvwriter_deployment = ""
'''
first_run = True
first_run_dep = True
for csv_files in glob.glob("*.csv"):
    if csv_files == "jboss_states.csv":
        first_run = False
    if csv_files == "jboss_deployment_states.csv":
        first_run_dep = False


csvwriter = csv.writer(file('jboss_states.csv', 'ab'))

csvwriter_deployment = csv.writer(file('jboss_deployment_states.csv', 'ab'))
if first_run:
    csvwriter.writerow(['DATASOURCE NAME', 'STATE'])

if first_run_dep:
    csvwriter_deployment.writerow(['DEPLOYMENT NAME', 'STATE'])
'''
def set_up_csv_files(port):
    global csvwriter
    global csvwriter_deployment
    first_run = True
    first_run_dep = True
    for csv_files in glob.glob("*.csv"):
        if csv_files == "jboss_states" + port + ".csv":
            first_run = False
        if csv_files == "jboss_deployment_states" + port + ".csv":
            first_run_dep = False
    csvwriter = csv.writer(file('jboss_states' + port + '.csv', 'ab'))

    csvwriter_deployment = csv.writer(file('jboss_deployment_states' + port + '.csv', 'ab'))
    if first_run:
        csvwriter.writerow(['DATASOURCE NAME', 'STATE'])

    if first_run_dep:
        csvwriter_deployment.writerow(['DEPLOYMENT NAME', 'STATE'])
    

def run_deployment_state(jboss_command_list):
    command_list = jboss_command_list[:-1]
    command_list.append('deployment-info --name=*')
    fileptr = open('deployment_state.txt', 'wb')
    subprocess.Popen(command_list, stdout=fileptr, stderr=subprocess.STDOUT)
    time.sleep(2)
    with open('deployment_state.txt') as f:
        command_result = f.readlines()
        print command_result
        if len(command_result) < 2:
            return
        for each_line in command_result[1:]:
            status = each_line.split()
            name = status[0]
            state_status = status[-1]
            csvwriter_deployment.writerow([name, state_status])

def run_individual_commands(jboss_command_list, datasource):
    command_list = jboss_command_list[:-1]
    individual_param = '/subsystem=datasources/data-source=' + datasource + '/statistics=pool:write-attribute(name=statistics-enabled,value=true)'
    command_list.append(individual_param)
    print command_list
    fileptr = open('individual_buffer.txt', 'wb')
    subprocess.Popen(command_list, stdout=fileptr, stderr=subprocess.STDOUT)
    time.sleep(2)
    with open('individual_buffer.txt') as f:
        command_result = f.read()
        if 'success' in str(command_result):
            csvwriter.writerow([datasource.replace('"', ''), 'Active'])
        else:
            csvwriter.writerow([datasource.replace('"', ''), 'In-Active'])


def parse_jboss_result(jboss_command_list, logfile):
    with open(logfile) as f:
        all_content = f.readlines()
    for each_line in all_content[4:]:
        if '}' in each_line:
            break
        each_line = each_line.replace(' ', '')
        each_line = each_line.split('=>')[0]
        print each_line
        run_individual_commands(jboss_command_list, each_line) 


def run_jboss_commands(jboss_command_list):
    fileptr = open('jbosslog.txt', 'wb')
    command_out = subprocess.Popen(jboss_command_list, stdout=fileptr, stderr=subprocess.STDOUT)
    time.sleep(2)
    parse_jboss_result(jboss_command_list, 'jbosslog.txt')



if __name__ == '__main__':
    controller = raw_input("Enter port number: ")
    if controller != "":
        jboss_command_list = ['/eap/eap-6.4/bin/jboss-cli.sh', '--connect', 'controller=localhost:' + controller, '--user=admin', '--password=password', '-c', '/subsystem=datasources:read-resource']
    else:
        jboss_command_list = ['/eap/eap-6.4/bin/jboss-cli.sh', '--connect', '--user=admin', '--password=password', '-c', '/subsystem=datasources:read-resource']
    set_up_csv_files(controller)
    run_jboss_commands(jboss_command_list)
    run_deployment_state(jboss_command_list)
