"use strict";
var last_storage_get_ptr, last_storage_get_len;
function storage(importObject) {
  importObject.env.test_rpg_storage_get = function(keyPtr,keyLen) {
    var key=UTF8ToString(keyPtr,keyLen);
    var v=null;
    try{
      v = window.localStorage.getItem(key);
    } catch(e) {
      v=null;
    }
    if(v===null){
      return -1;
    }
    var bytes=new TextEncoder().encode(v);
    var p=wasm_exports.allocate_vec_u8(bytes.length);
    new Uint8Array(wasm_memory.buffer,p,bytes.length).set(bytes);
    last_storage_get_ptr=p;last_storage_get_len=bytes.length;
    return bytes.length;
  };
  importObject.env.test_rpg_storage_get_ptr = function(){
    return last_storage_get_ptr;
  },
  importObject.env.test_rpg_storage_set = function(keyPtr,keyLen,valPtr,valLen) {
    var key=UTF8ToString(keyPtr,keyLen);
    var val=UTF8ToString(valPtr,valLen);
    try{
      window.localStorage.setItem(key,val);
      return 1;
    }catch(e){
      return 0;
    }
  }
}

miniquad_add_plugin({register_plugin: storage});
