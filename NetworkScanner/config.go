package main

import (
	"os"
	"encoding/json"
	"io/ioutil"

	log "github.com/sirupsen/logrus"
)

// Users struct which contains
// an array of users
type Config struct {
    Url string `json:"url"`
}

// Exists reports whether the named file or directory exists.
func Exists(name string) bool {
	result := false
	log.Debug("We have been asked to check if this exists: ", name)
	file, err := os.Stat(name)
	if err == nil {
		if os.IsNotExist(err) {
			log.Warn("File doesn't exist: ", file)
		} else {
			isFile := checkType(file)
			log.Debug("Is it a file: ", *isFile)
			if *isFile == 2 {
				result = true
			}
		}
	}
	return result
}

func checkType(fi os.FileInfo) *int {
	format := 0

	switch mode := fi.Mode(); {
	case mode.IsDir():
		format = 1
	case mode.IsRegular():
		format = 2
	}

	return &format
}

func GetData(data *Config, file string) bool {
	validConfig := false
	f, err := os.Open(file)
	if err != nil {
		log.Warn("Failed to open file err: ", err)
	} else {
		byteValue, _ := ioutil.ReadAll(f)
		json.Unmarshal(byteValue, &data)
		log.Debug(data)
		if err != nil {
			log.Warn("Couldn't edit file: ", err, f)
		} else {
			validConfig = true
		}
	}
	return validConfig
}