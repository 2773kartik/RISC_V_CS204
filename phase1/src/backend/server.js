const express = require('express');
const { spawn } = require('child_process');
var app = express();

app.use(function (req, res, next) {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});
app.use(express.json())

app.get('/api/run-cpp', (req, res) => {
  const cpp = spawn('./a.exe', []);

  let result = "";
  
  cpp.stdout.on('data', (data) => {
    console.log(`Received data from C++ code: ${data}`)
    result += data.toString();
  });

  cpp.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  cpp.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    res.send(result);
  });
});

app.listen(process.env.PORT || 5000, () => {
  console.log(`Backend server listening on port ${process.env.PORT || 5000}`);
});
