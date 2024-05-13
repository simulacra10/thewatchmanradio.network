//import express,create the app variable

const express = require('express');
const req = require('express/lib/request');
const res = require('express/lib/response');
const app = express();
const path = require('path');
const port = process.env.PORT || 3300;
//app.set('view engine', 'ejs')   

//app.get('/', (req,res) => {
//    res.render('index')
//})

app.use(express.static(path.join(__dirname, 'public')));

//use "npm run start" in the terminal to start the express server
app.listen(port)
console.log("Server is listing on port 3300")
