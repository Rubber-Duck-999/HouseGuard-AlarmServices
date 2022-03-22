package main

// Mostly based on https://github.com/golang/net/blob/master/icmp/ping_test.go
// All ye beware, there be dragons below...

import (
	"context"
	"io/ioutil"
	"net/http"
	"os/exec"
	"strings"
	"time"

	"github.com/Ullaakut/nmap"
	log "github.com/sirupsen/logrus"
)

const (
	ProtocolICMP = 1
)

// Default to listen on all IPv4 interfaces
var ListenAddr = "0.0.0.0"

func (scan *Scan) resetDevices() {
	for id := range scan.Devices {
		scan.Devices[id].Alive = false
	}
}

func (scan *Scan) nmapScan() {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	// Equivalent to `/usr/local/bin/nmap -p 80,443,843 google.com facebook.com youtube.com`,
	// with a 2 minute timeout.
	scanner, err := nmap.NewScanner(
		nmap.WithTargets("192.168.0.0/24"),
		nmap.WithPorts("22,80,443,843,32400"),
		nmap.WithContext(ctx),
	)
	if err != nil {
		log.Error("Unable to create nmap scanner: ", err)
	}

	result, warnings, err := scanner.Run()
	if err != nil {
		log.Error("Unable to run nmap scan: ", err)
	}

	if warnings != nil {
		log.Error("Warnings: ", warnings)
	}

	log.Debug("Nmap scan done: ", len(result.Hosts), " hosts up scanned in seconds ", result.Stats.Finished.Elapsed)
	// Use the results to print an example output
}

func (scan *Scan) runARP() {
	data, err := exec.Command("arp", "-a").Output()
	if err != nil {
		log.Error(err)
	}

	for _, line := range strings.Split(string(data), "\n") {
		fields := strings.Fields(line)
		if len(fields) < 3 {
			continue
		}

		// strip brackets around IP
		ip := strings.Replace(fields[1], "(", "", -1)
		ip = strings.Replace(ip, ")", "", -1)
		new_device := true
		mac := fields[3]
		for id := range scan.Devices {
			if scan.Devices[id].Mac == mac {
				new_device = false
				log.Trace("Device found in Arp table")
				scan.Devices[id].Ip = ip
				scan.Devices[id].Alive = true
				time.Sleep(1 * time.Second)
			}
		}
		if new_device {
			if mac != "<incomplete>" {
				log.Trace("Adding device ip: ", ip)
				response, err := http.Get("https://api.macvendors.com/" + mac)
				if err != nil {
					log.Error("Set back to start on MAC")
				} else {
					defer response.Body.Close()
					data, _ := ioutil.ReadAll(response.Body)

					if response.StatusCode != 200 {
						log.Error("Error on Name")
						data = []byte("Name not Found")
					}

					device := Device{string(data), mac, ip, true, UNKNOWN}
					scan.Devices = append(scan.Devices, device)
					scan.sendNewDevice(device)
					time.Sleep(1 * time.Second)
				}
			}
		}
	}
	for id := range scan.Devices {
		log.Debug("Device: ",
			scan.Devices[id].Ip, ", ",
			scan.Devices[id].Name, ", ",
			scan.Devices[id].Mac, ", ",
			scan.Devices[id].Alive)
		if scan.Devices[id].Alive == true {
			scan.updateDevice(scan.Devices[id].Name, "1")
		} else {
			scan.updateDevice(scan.Devices[id].Name, "0")
		}
		time.Sleep(1 * time.Second)
	}
}

func (scan *Scan) checkDevices() {
	for {
		log.Debug("### Start of Scan ###")
		scan.resetDevices()
		scan.nmapScan()
		scan.runARP()
		log.Warn("Number of devices: ", len(scan.Devices))
		alive := 0
		for id := range scan.Devices {
			if scan.Devices[id].Alive {
				alive = alive + 1
			}
		}
		log.Warn("Number of devices Alive: ", alive)
		log.Debug("### End of Scan ###")
		time.Sleep(30 * time.Second)
	}
}
