import * as pulumi from '@pulumi/pulumi';
import * as gcp from '@pulumi/gcp';

const network = new gcp.compute.Network('network');
const computeFirewall = new gcp.compute.Firewall('firewall', {
    network: network.id,
    sourceRanges: ['0.0.0.0/0'],
    allows: [{
        protocol: 'tcp',
        ports: ['22', '40000'],
    }],
});

const startupScript = `
#!/bin/bash
cd /home/runner/cloud-node
pip install -r ../requirements.txt >/home/runner/install-log.txt 2>&1
export PYTHONPATH=/home/runner:$PYTHONPATH
nohup python3 main.py >/home/runner/logs.txt 2>&1 &  
`;

// Create a Virtual Machine Instance
const computeInstance = new gcp.compute.Instance('instance', {
    machineType: 'e2-medium',
    bootDisk: {initializeParams: {image: 'debian-cloud/debian-11'}},
    metadataStartupScript: startupScript,
    networkInterfaces: [{
        network: network.id,
        // accessConfigus must include a single empty config to request an ephemeral IP
        accessConfigs: [{}],
    }],
});

export const instanceName = computeInstance.name;
export const instanceZone = computeInstance.zone;
export const instanceProject = computeInstance.project;
export const instanceIP = computeInstance.networkInterfaces.apply(ni => ni[0]?.accessConfigs?.[0].natIp);
