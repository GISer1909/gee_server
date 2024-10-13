const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const { spawn } = require('child_process');
const fs = require('fs');
const config = require('./config.json')

const app = express();


app.use(bodyParser.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.send('The server is running')
})

app.get('/searchByPoint', execPythonScript('search_gee_point.py'));
app.get('/searchByBbox', execPythonScript('search_gee_bbox.py'));

const expressWs = require('express-ws');
expressWs(app);

app.ws('/download', (ws, req) => {
    // Get the scene ID from the query string.
    const image_id = req.query.image_id;
    if (!image_id) {
        ws.send('No scene ID provided.');
        return ws.close();

    }
    const bands = req.query.bands;
    if (!bands || bands == "") {
        ws.send('No bands provided.');
        return ws.close();

    }
    const python = spawn('python', ['download_gee.py', '--image_id', image_id, '--bands', bands]);

    python.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        ws.send(`${data}`);
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        ws.send(`${data}`);
    });

    python.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        ws.close();
    });
    //当ws close时，关闭python程序
    ws.on('close', (data) => {
        console.log('WebSocket connection closed', data);
        python.kill();
        if (data == 4999) {
            //删除文件
            try {
                setTimeout(() => {
                    fs.unlinkSync(`./public/${image_id.replaceAll('/', '_')}.tif`);
                }, 1000);
            } catch (error) {
                console.log(error);
            }

        }
    });
});
app.get('/download', (req, res) => {
    const { image_id } = req.query;
    const { bands } = req.query;
    if (!image_id) {
        res.json({
            code: 500,
            message: 'No scene ID provided.'
        });

    }
    if (!bands || bands == "") {
        res.json({
            code: 500,
            message: 'No bands provided.'
        });

    }
    const python = spawn('python', ['download_gee.py', '--image_id', image_id, '--bands', bands]);
    python.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        res.write(`${data}`);
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        res.write(`${data}`);
    });

    python.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        res.write(`request completed`);
        res.end()
    });

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
});

app.post('/download2', (req, res) => {
    const { dataset, day, coord_str, band_index_exp } = req.body;

    if (!dataset || !day || !coord_str) {
        res.status(400).json({
            message: 'Missing required parameters.'
        });
        return;
    }

    const python = spawn('python', ['download2.py', '--dataset', dataset, '--day', day, '--coord_str', coord_str, '--band_index_exp', band_index_exp]);
    console.log('python download2.py --dataset', dataset, '--day', day, '--coord_str', coord_str, '--band_index_exp', band_index_exp)
    let result = '';

    python.stdout.on('data', (data) => {
        result += data.toString();
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    python.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        res.send(result);
    });
});



app.listen(config.port, () => {
    console.log('Server is running on port 1337');
});

function execPythonScript(scriptName) {
    return (req, res) => {
        //是否有参数:start_date,end_date,cloud_cover,dataset
        if (req.query.start_date == undefined || req.query.end_date == undefined || req.query.max_cloud_cover == undefined || req.query.dataset == undefined) {
            return res.json({
                code: 500,
                message: '参数不全'
            });
        }
        //if is point search, check lat and lon
        if (scriptName == 'search_gee_point.py') {
            if (req.query.latitude == undefined || req.query.longitude == undefined) {
                return res.json({
                    code: 500,
                    message: '参数不全'
                });
            }
        }
        //if is bbox search, check xmin, ymin, xmax, ymax
        if (scriptName == 'search_gee_bbox.py') {
            if (req.query.xmin == undefined || req.query.ymin == undefined || req.query.xmax == undefined || req.query.ymax == undefined) {
                return res.json({
                    code: 500,
                    message: '参数不全'
                });
            }
        }

        const command = `python ./${scriptName} ${generateCommandArguments(req.query)}`;
        console.log(command)
        exec(command, { maxBuffer: 2000 * 1024 }, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return res.json({
                    code: 500,
                    message: '服务器错误'
                });
            }

            res.json({
                code: 200,
                message: '查询成功',
                data: JSON.parse(stdout)
            });
        });
    };
}

function generateCommandArguments(body) {
    return Object.entries(body)
        .map(([key, value]) => `--${key} ${value}`)
        .join(' ');
}


