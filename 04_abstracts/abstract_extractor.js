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
  // 1) ScienceDirect/Elsevier —— 只取 div.abstract.author,排除嵌套在 Highlights/graphical 里的块,优先标题=Abstract(修复 Highlights 误抓)
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
  if(!txt){ el=document.querySelector('[data-test="abstract-content"], #Abs1-content, section[data-title="Abstract"] .c-article-section__content'); txt=clean(el); } // 2) Springer/Nature
  if(!txt){ el=document.querySelector('.art-abstract, section.html-abstract, #html-abstract'); txt=clean(el); }                                                          // 3) MDPI
  if(!txt){ el=document.querySelector('section.article-section__abstract .article-section__content, .abstract-group .article-section__content'); txt=clean(el); }        // 4) Wiley
  if(!txt){ el=document.querySelector('.hlFld-Abstract, .abstractSection, .abstractInFull'); txt=clean(el); }                                                            // 5) Atypon: T&F/ASCE/SAGE
  if(!txt){ el=document.querySelector('.wd-jnl-art-abstract, div[itemprop="description"], .article-text'); txt=clean(el); }                                               // 6) IOP
  if(!txt){ el=document.querySelector('.abstract-text'); txt=clean(el); }                                                                                                 // 7) IEEE
  if(!txt){                                                                                                                                                                // 8) meta 兜底
    var ms=['meta[name="citation_abstract"]','meta[name="dc.Description"]','meta[name="dc.description"]','meta[property="og:description"]','meta[name="description"]'];
    for(var k=0;k<ms.length && !txt;k++){ var m=document.querySelector(ms[k]); if(m && m.content && m.content.trim().length>140) txt=m.content.trim().replace(/\s+/g,' '); }
  }
  if(!txt){                                                                                                                                                                // 9) 标题==Abstract 兜底
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
