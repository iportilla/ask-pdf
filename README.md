# Ask PDF Demo

For details about using this service, see [details.md](details.md)



## Building and Publishing

**Note:** Get and OpenAI API key and  then:

1. Connect to the AWS vm used in class
```bash
ssh ubuntu@XX.XXX.XXX.XXX
```

2. Change directories to your own directory on this cloud VM

```bash
cd MYNAME_DIR
```

3. Clone this repo with:

```bash
git clone https://github.com/iportilla/ask-pdf.git
```

4. Change directoris and Copy `.env.sample` to `.env` with:

```bash
cd ask-pdf/
cp .env.sample .env
```

5. Get your own `API key` from [openAI](https://platform.openai.com/account/api-keys) web site

`
https://platform.openai.com/account/api-keys
`

6. Update `.env` file with your *OpenAI Key* value:

```bash
vi .env
API_KEY="YOUR_API_KEY"
```
7. Update port number (range: 80-90) in `Makefile` file

```bash
vi Makefile
export PORT ?= 81 

#Any port value between 80-90
```


8. Run

```bash
make clean
make build
make run
```

*Notice* that it will take 4-5 minutes to complete `make build`, 


9. Open a browser to

`XX.XXX.XXX.XXX:PORT`

10. Click on `upload File`, to try this app.  (you can use the US Constitution provided in docs)

11. Ask a question like: `Who can be a representative?`
