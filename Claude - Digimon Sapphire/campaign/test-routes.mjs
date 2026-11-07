import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
const catalog=JSON.parse(readFileSync(new URL('./digimon.json',import.meta.url)));
const {maps}=JSON.parse(readFileSync(new URL('./routes.json',import.meta.url)));
for(const map of Object.values(maps).filter(m=>m.tiles)){
 test(`${map.id}: dimensions, reachable events, warps and encounters`,()=>{
  assert.equal(map.tiles.length,map.height);for(const row of map.tiles)assert.equal(row.length,map.width);
  const walk=(x,y)=>map.walkableTiles.includes(map.tiles[y]?.[x]);const seen=new Set(),queue=[[12,9]];
  while(queue.length){const [x,y]=queue.pop(),key=`${x},${y}`;if(seen.has(key)||!walk(x,y))continue;seen.add(key);queue.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);}
  for(const event of map.events){assert(seen.has(event.at.join(',')),event.id);if(event.kind==='warp'){assert(maps[event.toMap]);const target=maps[event.toMap];assert(target.walkableTiles.includes(target.tiles[event.to[1]][event.to[0]]));assert.equal(target.journey,map.journey);}if(event.formId)assert(catalog.forms[event.formId]);for(const mon of event.team??[])assert(catalog.forms[mon.formId]);}
  if(map.encounters.length)assert.equal(map.encounters.reduce((sum,row)=>sum+row.weight,0),100);
  for(const row of map.encounters){assert(catalog.forms[row.formId]);assert(row.minLevel<=row.maxLevel&&row.minLevel>=1&&row.maxLevel<=100);assert(row.weight>0);}
 });
}
