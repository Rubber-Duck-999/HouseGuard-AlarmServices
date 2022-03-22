package main

type Device struct {
	Name    string `json:"Name"`
	Mac     string `json:"Mac"`
	Ip      string `json:"Ip"`
	Alive   bool   `json:"Alive"`
	Allowed int    `json:"Allowed"`
}

type Scan struct {
	Devices []Device `json:"Devices"`
	Count   int      `json:"Count"`
	Url     string   `json:"url"`
}

const ALLOWED int = 1
const BLOCKED int = 2
const UNKNOWN int = 3
