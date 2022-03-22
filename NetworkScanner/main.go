package main

import (
	"fmt"
	"os"
	"os/user"
	log "github.com/sirupsen/logrus"
)

func main() {
	log.SetLevel(log.DebugLevel)
	customFormatter := new(log.TextFormatter)
	customFormatter.TimestampFormat = "2006-01-02 15:04:05"
	log.SetFormatter(customFormatter)
	customFormatter.FullTimestamp = true
	log.Warn("NetworkScanner - Beginning to run Network Scanner Program")

	var data Config
	user, err := user.Current()
	if err != nil {
		log.Fatalf(err.Error())
	}
	username := user.Username
	file := "config.json"
	path := fmt.Sprintf("/home/%s/sync/", username) + file
	if Exists(path) {
		GetData(&data, path)
	} else {
		if Exists(file) {
			GetData(&data, file)
		} else {
			log.Error("File doesn't exist")
			os.Exit(2)
		}
	}
	a := make([]Device, 0)
	scan := Scan{
		Devices: a,
		Count:   0,
	}
	err = scan.getDevices(data.Url)
	if err != nil {
		log.Error("Error found on api GET")
	} else {
		scan.checkDevices()
	}
}
