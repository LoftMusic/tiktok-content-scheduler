// bg.js - Simple Audio Recorder
var rec = false;
var mr = null;
var chunks = [];
var strm = null;

chrome.action.onClicked.addListener(function(tab) {
    if (rec) {
        if (mr && mr.state === 'recording') mr.stop();
    } else {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs && tabs[0]) start(tabs[0].id);
        });
    }
});

function start(tabId) {
    chrome.tabCapture.capture({audio: true, video: false}, function(stream) {
        if (!stream || stream.getAudioTracks().length === 0) return;
        
        strm = stream;
        mr = new MediaRecorder(stream, {mimeType: 'audio/webm'});
        chunks = [];
        
        mr.ondataavailable = function(e) { 
            if (e.data.size > 0) chunks.push(e.data); 
        };
        
        mr.onstop = function() {
            if (chunks.length > 0) {
                var b = new Blob(chunks, {type: 'audio/webm'});
                chrome.downloads.download({
                    url: URL.createObjectURL(b),
                    filename: 'recording_' + Date.now() + '.webm',
                    saveAs: true
                });
            }
            if (strm) strm.getTracks().forEach(function(t) { t.stop(); });
            rec = false;
            chrome.action.setBadgeText({text: ''});
        };
        
        mr.start(100);
        rec = true;
        chrome.action.setBadgeText({text: 'REC'});
        chrome.action.setBadgeBackgroundColor({color: '#f38ba8'});
    });
}
