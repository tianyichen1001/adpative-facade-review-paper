# Abstract-scraping worker instructions

You are a Chrome web-scraping worker. Extract the Abstract body for each DOI in your assigned shard and save a JSON slice. Be robust: if one DOI fails, continue with the rest. Work ONLY in your own browser tab. Your spawn message gives two values: PUB and SHARD (e.g. `PUB=elsevier SHARD=15`).

Constants:
- BASE_DIR = C:\Users\ASUS\AppData\Roaming\Claude\local-agent-mode-sessions\d726a80c-c79c-4c6f-8aae-4437cb3fa6aa\6c47fac8-c837-4eea-9f3e-5bcbe5129e7b\local_8d189bd4-6511-401e-b559-d2f2bf67ca55\outputs\04_abstracts
- DEVICE_ID = 2cae1489-6f64-49b7-a952-a52820db9ecd

Build your two paths from PUB and SHARD:
- SHARD_INPUT  = BASE_DIR\scrape_inputs\{PUB}_shard{SHARD}.csv   (e.g. ...\scrape_inputs\elsevier_shard15.csv)
- SLICE_OUTPUT = BASE_DIR\slice_{PUB}_{SHARD}.json              (e.g. ...\slice_elsevier_15.json)

## Setup (once, in order)
1. Load browser tools — call ToolSearch with query:
   select:mcp__Claude_in_Chrome__list_connected_browsers,mcp__Claude_in_Chrome__select_browser,mcp__Claude_in_Chrome__tabs_context_mcp,mcp__Claude_in_Chrome__tabs_create_mcp,mcp__Claude_in_Chrome__navigate,mcp__Claude_in_Chrome__javascript_tool,mcp__Claude_in_Chrome__get_page_text   (max_results 10)
   You also have Read, Write, and the bash tool already.
2. list_connected_browsers → select_browser(DEVICE_ID) → tabs_context_mcp(createIfEmpty:true) → tabs_create_mcp. Save the tabId returned by tabs_create_mcp; pass it on EVERY navigate / javascript_tool / get_page_text call. Never act on another tab.

## Read input
Use the Read tool on SHARD_INPUT. It is a CSV with header `doi,doi_url`. Process every row.

## Per DOI (doi, doi_url)
1. navigate(url=doi_url, tabId=yourTab)
2. bash `sleep 7`   (let DOI redirect resolve)
3. javascript_tool(action:"javascript_exec", tabId:yourTab, text: <the Cropping JS at the bottom>). It returns ONE token: STATE_OK / STATE_CF / STATE_BOT / STATE_REDIR / STATE_NOABS.
4. Handle the token:
   - STATE_OK   → get_page_text(tabId:yourTab). Take the substring strictly between the markers `ZABSTRACTZ` and `ZENDZ`, strip whitespace → result[doi] = that text. If the returned text has no `ZABSTRACTZ`, re-run the JS once, then get_page_text again.
   - STATE_REDIR→ bash `sleep 4`, re-run the JS. Up to 5 tries total. Still REDIR → skip this DOI.
   - STATE_CF or STATE_BOT → bash `sleep 20`, re-run the JS. Up to 5 tries total. NEVER solve a captcha/challenge or click anything. Still blocked → skip.
   - STATE_NOABS→ may be lazy-loading. bash `sleep 4`, re-run the JS 1-2 more times. Still NOABS → skip.
   - JS error / non-STATE value → bash `sleep 5`, retry once; else skip.
5. CRITICAL: never use the JS return value as the abstract text (it is only a status). Always get the abstract via get_page_text after STATE_OK.

## Output
Use the Write tool to write EXACTLY the file path SLICE_OUTPUT.
Content: one valid JSON object (UTF-8) mapping each SUCCESSFUL doi (string) → its abstract (string). Include only successes. If zero successes, write `{}`.

## Reply
Reply with ONLY one line: `extracted: N, skipped: M` then the comma-separated list of skipped DOIs. Do NOT put any abstract text in your reply.

## Cropping JS (run exactly this; do not modify)
(function(){
  var t=(document.title||'').toLowerCase(), host=location.hostname;
  if(/just a moment|attention required|verify you|checking your browser/.test(t)) return 'STATE_CF';
  if(host.indexOf('perfdrive')>-1 || /bot manager|are you a robot/.test(t)) return 'STATE_BOT';
  if(host.indexOf('linkinghub')>-1 || /redirecting/i.test(t)) return 'STATE_REDIR';
  function clean(el){
    if(!el) return null;
    var c=el.cloneNode(true);
    c.querySelectorAll('h1,h2,h3,h4,.section-title,.sectionHeading,.abstractKeywords,.kwd-group,.c-article-section__title,figure,figcaption').forEach(function(e){e.remove();});
    var s=((c.innerText||c.textContent||'')).replace(/^\s*abstract\s*/i,'').replace(/\s*keywords?:[\s\S]*$/i,'').replace(/\s+/g,' ').trim();
    return s.length>80 ? s : null;
  }
  var txt=null, el;
  var cands=[].slice.call(document.querySelectorAll('div.abstract.author')).filter(function(b){
    var c=(b.className||'').toLowerCase();
    if(c.indexOf('highlight')>-1 || c.indexOf('graphical')>-1) return false;
    if(b.closest && b.closest('.author-highlights, .graphical')) return false;
    return true;
  });
  var pick=null;
  cands.forEach(function(b){ if(pick) return; var h=b.querySelector('h2,h3'); if(h && h.textContent.trim().toLowerCase()==='abstract') pick=b; });
  if(!pick && cands.length){ cands.sort(function(a,b){return (b.innerText||'').length-(a.innerText||'').length;}); pick=cands[0]; }
  if(pick) txt=clean(pick);
  if(!txt){ el=document.querySelector('[data-test="abstract-content"], #Abs1-content, section[data-title="Abstract"] .c-article-section__content'); txt=clean(el); }
  if(!txt){ el=document.querySelector('.art-abstract, section.html-abstract, #html-abstract'); txt=clean(el); }
  if(!txt){ el=document.querySelector('section.article-section__abstract .article-section__content, .abstract-group .article-section__content'); txt=clean(el); }
  if(!txt){ el=document.querySelector('.hlFld-Abstract, .abstractSection, .abstractInFull'); txt=clean(el); }
  if(!txt){ el=document.querySelector('.wd-jnl-art-abstract, div[itemprop="description"], .article-text'); txt=clean(el); }
  if(!txt){ el=document.querySelector('.abstract-text'); txt=clean(el); }
  if(!txt){
    var ms=['meta[name="citation_abstract"]','meta[name="dc.Description"]','meta[name="dc.description"]','meta[property="og:description"]','meta[name="description"]'];
    for(var k=0;k<ms.length && !txt;k++){ var m=document.querySelector(ms[k]); if(m && m.content && m.content.trim().length>140) txt=m.content.trim().replace(/\s+/g,' '); }
  }
  if(!txt){
    var hs=[].slice.call(document.querySelectorAll('h1,h2,h3,h4,strong,b,dt'));
    for(var j=0;j<hs.length && !txt;j++){
      if(hs[j].textContent.trim().toLowerCase()==='abstract'){
        var sib=hs[j].nextElementSibling, acc='';
        while(sib && !/^h[1-4]$/i.test(sib.tagName||'')){ acc+=' '+((sib.innerText)||''); sib=sib.nextElementSibling; }
        acc=acc.replace(/\s+/g,' ').trim(); if(acc.length>140) txt=acc;
      }
    }
  }
  if(!txt) return 'STATE_NOABS';
  while(document.body.firstChild) document.body.removeChild(document.body.firstChild);
  var art=document.createElement('article'), p=document.createElement('p');
  p.textContent='ZABSTRACTZ '+txt+' ZENDZ'; art.appendChild(p); document.body.appendChild(art);
  return 'STATE_OK';
})()
