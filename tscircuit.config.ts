// Runtime platform settings belong in the TS config: this pinned CLI strips
// platformConfig from its JSON schema. Explicit null prevents all routing caches.
export default {
  platformConfig: {
    partsEngineDisabled: false,
    enablePartOrientationAnalysis: true,
    useCloudAutorouter: false,
    localCacheEngine: null,
    autorouterThreads: 1,
  },
}
