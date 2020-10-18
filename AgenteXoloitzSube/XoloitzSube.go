package main

import (
	"fmt"
	"log"
	"os"
	"time"
	"math/rand"
	"math"
	"strconv"
	"strings"
	"path/filepath"
	"regexp"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/common-nighthawk/go-figure"
	"github.com/fsnotify/fsnotify"
)

func waitUntilFind(filename string) error {
	for {
		time.Sleep(1 * time.Second)
		_, err := os.Stat(filename)
		if err != nil {
			if os.IsNotExist(err) {
				continue
			} else {
				return err
			}
		}
		break
	}
	return nil
}

func getid() string {
	t := time.Now()
	valueTime := t.Format(time.RFC3339)
	splitFecha := strings.Split(valueTime,"T")
	fecha := splitFecha[0]
	horasplit := strings.Split(splitFecha[1],"-")
	fechid := strings.Replace(fecha,"-","",-1)
	horaMinSegid := strings.Replace(horasplit[0],":","",-1)
	miliseg := strings.Replace(horasplit[1],":","",-1)
	alnums := strconv.Itoa((int(math.Round(rand.Float64() * 100000))))

	return "_"+fechid+"_"+horaMinSegid+"_"+miliseg+"_"+alnums
}

func main() {
	
	myFigure := figure.NewFigure("Welcome to XoloitzSube", "", true)
  	myFigure.Print()

	if len(os.Args) != 4 {
		fmt.Printf("usage: %s <bucket> <filename> <region>\n", filepath.Base(os.Args[0]))
		os.Exit(1)
	}

	bucket := os.Args[1]
	filename := os.Args[2]
	region := os.Args[3]

	fmt.Println(bucket)
	fmt.Println(filename)
	fmt.Println(region)
	
	err := waitUntilFind(filename)
	if err != nil {
		log.Fatalln(err)
	}

	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatalln(err)
	}
	defer watcher.Close()

	err = watcher.Add(filename)
	if err != nil {
		log.Fatalln(err)
	}

	renameCh := make(chan bool)
	removeCh := make(chan bool)
	errCh := make(chan error)

	go func() {
		for {
			select {
			case event := <-watcher.Events:
				switch {
				case event.Op&fsnotify.Write == fsnotify.Write:
					// log.Printf("Write:  %s: %s", event.Op, event.Name)
				case event.Op&fsnotify.Create == fsnotify.Create:

					if(strings.HasSuffix(event.Name,".wav")){
						pathWithoutSpace := strings.Replace(event.Name," ","",-1)
						reg, err := regexp.Compile("[^a-zA-Z0-9/.]+")
						if err != nil {
							log.Fatal(err)
						}
						processedString := reg.ReplaceAllString(pathWithoutSpace, "")
						log.Printf("Create: %s", event.Name )
						processedString_id := strings.Replace(processedString,".wav",getid()+".wav",-1) 
						log.Printf("S3 Name: %s", processedString_id )
						

						file, err := os.Open(event.Name)
						if err != nil {
							fmt.Println("Failed to open file", filename, err)
						}
						defer file.Close()
						conf := aws.Config{Region: aws.String(region), Credentials: credentials.AnonymousCredentials}
						sess := session.New(&conf)
						svc := s3manager.NewUploader(sess)
						
						if err == nil {

							fmt.Println("Uploading file to S3...")
							result, err := svc.Upload(&s3manager.UploadInput{
								Bucket: aws.String(bucket),
								Key:    aws.String(filepath.Base(processedString_id)),
								ACL:                  aws.String("public-read-write"),
								Body:   file,
							})
							if err != nil {
								fmt.Printf("error when try to upload uploaded %s to %s, error %s\n",  filename, result.Location, err)
							}
							fmt.Printf("Successfully uploaded %s to %s\n", filename, result.Location)

						}

						

					}
					
				case event.Op&fsnotify.Remove == fsnotify.Remove:
					// log.Printf("Remove: %s: %s", event.Op, event.Name)
					removeCh <- true
				case event.Op&fsnotify.Rename == fsnotify.Rename:
					// log.Printf("Rename: %s: %s", event.Op, event.Name)
					renameCh <- true
				case event.Op&fsnotify.Chmod == fsnotify.Chmod:
					// log.Printf("Chmod:  %s: %s", event.Op, event.Name)
				}
			case err := <-watcher.Errors:
				errCh <- err
			}
		}
	}()

	go func() {
		for {
			select {
			case <-renameCh:
				err = waitUntilFind(filename)
				if err != nil {
					log.Fatalln(err)
				}
				err = watcher.Add(filename)
				if err != nil {
					log.Fatalln(err)
				}
			case <-removeCh:
				err = waitUntilFind(filename)
				if err != nil {
					log.Fatalln(err)
				}
				err = watcher.Add(filename)
				if err != nil {
					log.Fatalln(err)
				}
			}
		}
	}()

	log.Fatalln(<-errCh)
}