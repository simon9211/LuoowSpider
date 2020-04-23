const fs = require('node-fs-extra');
const db = require('mongodb').MongoClient;

let col, single;
db.connect('mongodb://localhost:27017/waasaa', function (error, db) {
    if (error) throw new Error(error);
    col = db.collection('col');
    single = db.collection('single');
});


function getCols() {
    return new Promise((resolve, reject) => {
        let retryTimes = 0;
        let timer;
        if (!col)
            timer = setInterval(function () {
                if (retryTimes > 20)
                    return reject('Database not available now.');
                console.log('Waiting for database. Retry 200ms later.');
                if (col) {
                    exec(resolve, reject);
                    clearInterval(timer);
                }
            }, 200);
        else exec(resolve, reject)
    }).then((doc) => {
        for (let index = 0; index < doc.length; index++) {
            console.log(doc[index]['href']);
            // doc[index]['href']
            // getSingles(doc[index]['href'])
            single.find({href:doc[index]['href']}, { '_id': 0, }).
            toArray(async (error, doc) => {
                if (error) reject(error);
                // resolve(doc);
                for (let index = 0; index < doc.length; index++) {
                    
                    // downloadMp3(doc[index]['src'])
                    // doc[index]['href']
                    // var fileName = getHashCode(doc[index]['src']) + doc[index]['title']
                    var fileName = doc[index]['title']
                    downloadImg(doc[index]['src'],fileName,function(){
                        console.log(fileName + ' done');
                    });

                }

                // var fileName = getHashCode(doc[0]['href']) + doc[0]['title']
                //     downloadImg(doc[0]['src'],fileName,function(){
                //         console.log(fileName + ' done');
                //     });
            })
        }
    }
    );

    function exec(resolve, reject) {
        col.find({title:/李志/}, { '_id': 0, }).
            toArray(async (error, doc) => {
                if (error) reject(error);
                resolve(doc);
            })
    }
}

function parseUrlForFileName(address) {
    var filename = path.basename(address);
    return filename;
}

//获取字符串的 哈希值 
function getHashCode(str,caseSensitive){
    if(!caseSensitive){
        str = str.toLowerCase();
    }
    var hash  =   1315423911,i,ch;
    for (i = str.length - 1; i >= 0; i--) {
        ch = str.charCodeAt(i);
        hash ^= ((hash << 5) + ch + (hash >> 2));
    }
    return  (hash & 0x7FFFFFFF);
}

var request = require('request');
var path = require('path');
var ffs = require('fs');

var downloadImg = function(uri, filename, callback){
    let reg = /\\/g;
    //使用replace方法将全部匹配正则表达式的转义符替换为空
    uri = uri.replace(reg,'');
    // request.setHeader('referer','www.waasaa.com/')
    // request.get(uri: uri, headers: {
    //     'referer': 'https://www.waasaa.com/'
    //   }).pipe(ffs.createWriteStream(filename+'.mp3')).on('close', callback);
    request.head(uri,function(err, res, body){
    if (err) {
        console.log('err: '+ err);
        return false;
    }
    console.log('res: '+ res);
    request(uri).pipe(ffs.createWriteStream('images/'+filename+'.mp3')).on('close', callback);  //调用request的管道来下载到 images文件夹下
    });
};


function downloadMp3(url){
    // String.prototype.replaceAll = function(s1, s2) {
    //     return this.replace(new RegExp(s1, "gm"), s2);
    // }
    let reg = /\\/g;
    //使用replace方法将全部匹配正则表达式的转义符替换为空
    let replaceAfter = url.replace(reg,'');
    console.log(replaceAfter);
    var request = require('request');
    var req = request(replaceAfter, {timeout: 10000, pool: false});
    req.setMaxListeners(50);
    req.setHeader('user-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36');

    req.on('error', function(err) {
        throw err;
    });
    req.on('response', function(res) {
        res.setEncoding("binary");
        var fileData = "";

        res.on('data', function (chunk) {
            fileData+=chunk; 
        });
        res.on('end',function(){
            var name=url.slice(url.lastIndexOf("/"));
            var fileName="./"+name;

            fs.writeFile(fileName, fileData, "binary", function(err){
                if(err){
                    console.log("[downloadPic]文件   "+fileName+"  下载失败.");
                    console.log(err);
                }else{
                    console.log("文件"+fileName+"下载成功");
                }
            });  
        });
    })
}








function main() {
    // var profix = 'http://ting.xiai123.com/mp3/kewen/wysyy4s/Module0';
    // var appendixs = ['Unit1', 'Unit2', 'Words'];

    // for (var i = 1; i < 10; i++) {
    //     for (var j = 0; j < appendixs.length; j++) {
    //         var url = profix + i + '_' + appendixs[j] + ".mp3";
    //         downloadMp3(url);
    //     }
    // }

    const data = getCols()
    const d = JSON.stringify(data || 'error');
    console.log(data)
    console.log(d)
    //downloadMp3('http://ting.xiai123.com/mp3/kewen/wysyy4s/Module01_Unit2.mp3');
    // for (let index = 0; index < data.length; index++) {
    //     console.log(data[index]['href']);
    // }
}

// 开始
main();
