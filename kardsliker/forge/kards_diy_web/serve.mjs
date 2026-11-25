import http from "node:http";
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(".");
const port = Number(process.env.PORT ?? 5000);
const mime = {".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8",".png":"image/png",".jpg":"image/jpeg",".svg":"image/svg+xml",".json":"application/json"};
http.createServer((req,res)=>{
  let p = decodeURIComponent((req.url ?? "/").split("?")[0]);
  if (p === "/") p = "/index.html";
  const file = path.join(root,p);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end("Not found"); return; }
  res.setHeader("Content-Type", mime[path.extname(file)] ?? "application/octet-stream");
  fs.createReadStream(file).pipe(res);
}).listen(port,"127.0.0.1",()=>console.log(`Kards DIY: http://127.0.0.1:${port}`));
