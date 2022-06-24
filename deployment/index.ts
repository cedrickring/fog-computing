import * as pulumi from '@pulumi/pulumi';
import * as gcp from '@pulumi/gcp';

const network = new gcp.compute.Network('network');
const computeFirewall = new gcp.compute.Firewall('firewall', {
    network: network.id,
    sourceRanges: ['0.0.0.0/0'],
    allows: [{
        protocol: 'tcp',
        ports: ['22', '5000'],
    }],
});

// Create a Virtual Machine Instance
const computeInstance = new gcp.compute.Instance('instance', {
    machineType: 'e2-medium',
    bootDisk: {initializeParams: {image: 'debian-cloud/debian-11'}},
    networkInterfaces: [{
        network: network.id,
        // accessConfigus must include a single empty config to request an ephemeral IP
        accessConfigs: [{}],
    }],
});

export const instanceName = computeInstance.name;
export const instanceIP = computeInstance.networkInterfaces.apply(ni => ni[0]?.accessConfigs?.[0].natIp);
