/**
 * Google Apps Script — File Upload Handler
 * 
 * SETUP:
 * 1. Go to script.google.com → New project
 * 2. Paste this entire code
 * 3. Deploy → New deployment → Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 4. Copy the deployment URL and add it to your Streamlit secrets as "file_upload_url"
 */

// Your MI_Scout_Media folder ID
var FOLDER_ID = "1OLVXTd9ZkuDluGooDlKEr0gfDeopqppH";

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var fileName = data.fileName || "upload";
    var mimeType = data.mimeType || "application/octet-stream";
    var base64Data = data.fileData; // base64 encoded file content
    var playerName = data.playerName || "";
    
    // Decode base64
    var fileBlob = Utilities.newBlob(Utilities.base64Decode(base64Data), mimeType, fileName);
    
    // Get or create player subfolder
    var parentFolder = DriveApp.getFolderById(FOLDER_ID);
    var targetFolder = parentFolder;
    
    if (playerName) {
      var safeName = playerName.replace(/[^a-zA-Z0-9_\- ]/g, "").trim();
      var subFolders = parentFolder.getFoldersByName(safeName);
      if (subFolders.hasNext()) {
        targetFolder = subFolders.next();
      } else {
        targetFolder = parentFolder.createFolder(safeName);
      }
    }
    
    // Save file
    var file = targetFolder.createFile(fileBlob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    
    var response = {
      success: true,
      fileId: file.getId(),
      viewLink: "https://drive.google.com/file/d/" + file.getId() + "/view",
      folderLink: "https://drive.google.com/drive/folders/" + targetFolder.getId()
    };
    
    return ContentService.createTextOutput(JSON.stringify(response))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput("MI Scout File Upload endpoint is active.");
}
