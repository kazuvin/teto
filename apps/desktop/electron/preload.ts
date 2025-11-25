import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('electron', {
  // ここにElectronのAPIを公開
})
