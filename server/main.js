const Koa = require('koa');
const Router = require('koa-router');
const fs = require('fs');
const path = require('path');
const colors = require('colors');
const db = require('./db');
const config = () => require('./package.json');


const [app, router] = [new Koa(), new Router()];

router.get('/download/:platform', ctx => {
    const platform = parseInt(ctx.params.platform);
    const URL = `http://os3s219a3.bkt.clouddn.com/Luoo.qy-v${config().update.mainVersion}.0.${['dmg', 'exe', 'zip'][platform]}`;
    ctx.redirect(URL);
    log(`/download/${ctx.params.platform}`, ctx.request.ip)
});


router.get('/update/:platform/:preVersion', ctx => {
    const info = config().update;
    const preVersion = ctx.params.preVersion.split('.');

    if (parseInt(preVersion[0]) === info.mainVersion && parseInt(preVersion[1]) === info.updateVersion)
        ctx.body = JSON.stringify({ type: 'none' });

    else if (parseInt(preVersion[0]) !== info.mainVersion)
        ctx.body = JSON.stringify({
            type: 'full',
            version: `${info.mainVersion}.0`,
            url: `http://os3s219a3.bkt.clouddn.com/Luoo.qy-v${info.mainVersion}.0.${['dmg', 'exe', 'zip'][parseInt(ctx.params.platform)]}`,
            desc: info.mainDesc
        });

    else ctx.body = JSON.stringify({
            type: info.type,
            version: `${info.mainVersion}.${info.updateVersion}`,
            url: `http://os3s219a3.bkt.clouddn.com/update-v${info.mainVersion}.${info.updateVersion}.zip`,
            desc: info.updateDesc
        });
    log(`/update/${ctx.params.platform}/${ctx.params.preVersion}`, ctx.request.ip)
});

// 获取所有期刊
router.get('/periods', async ctx => {
    const data = await db.period.get();
    // let arr = data.map(item => item['period_name']);
    ctx.body = JSON.stringify(data || 'error');
    // log(`/single/${ctx.params.date}`, ctx.request.ip)
});

// 获取所有标签
router.get('/labels', async ctx => {
    const data = await db.label.get();
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
})

// 获取期刊里面所有专辑
router.get('/col/:peroid', async ctx => {
    // ctx.body = JSON.stringify(await db.single.getList(parseInt(ctx.params.preDate)));
    // const platform = parseInt(ctx.params.peroid);
    let param = ctx.params.peroid;
    const data = await db.col.get(param);
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
});

// 获取标签下所有的专辑
router.get('/col/tag/:tag', async ctx => {
    let param = ctx.params.tag;
    const data = await db.col.getLabel(param);
    // let arr = data.map(item => item['label_name']);
    ctx.body = JSON.stringify(data || 'error');
});

// 获取专辑里面所有的单曲
router.get('/singles/:col', async ctx => {
    ctx.body = JSON.stringify(await db.single.getList(ctx.params.col));
    //log(`/singles/${ctx.params.preDate}`, ctx.request.ip)
});



app.use(router.routes()).listen(config().config.port);
app.use(require('koa-static-server')({
    rootDir: path.join(__dirname, '../website'),
    index: 'index.html',
    gzip: true,
    maxage: 1000 * 60 * 60 * 24
}));


function log(api, ip) {
    ip = ip.split(':')[3];
    db.log(api, ip);
    console.log(`Response api  ${api.red}  to  ${ip.yellow}  at  ${(new Date()).toLocaleString().green}`)
}
