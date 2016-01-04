var neo4j = require('node-neo4j');
var fs = require('fs');
var AWS = require('aws-sdk');

var config = JSON.parse(fs.readFileSync('../config.json', 'utf8'));
var courseHomeContent = JSON.parse(fs.readFileSync('../data/courseHomeContent.json', 'utf8'));
var courseSyllabusContent = JSON.parse(fs.readFileSync('../data/courseSyllabusContent.json', 'utf8'));

var fin = buildContentJson();
var courseNames = Object.keys(fin);
var courseNamesSize = courseNames.length;
for (var j = 0; j < courseNamesSize; j++){
    s3upload('/MitContent', courseNames[j], fin[courseNames[j]]);
    console.log('uploaded content for course: ' + courseNames[j]);
}

function buildContentJson(){
    var final = {};
    var i;
    var result;
    var courseName;
    var courseHomeContentSize = courseHomeContent['pages'].length;
    for (i = 0; i < courseHomeContentSize; i++){
        result = courseHomeContent.pages[i].results[0];
        courseName = result.coursename;
        final[courseName] = result;
    }
    var courseSyllabusContentSize = courseSyllabusContent['pages'].length;
    for (i = 0; i < courseSyllabusContentSize; i++){
        result = courseSyllabusContent.pages[i].results[0];
        courseName = result.coursename;
        if (Object.keys(final).indexOf(courseName) >= 0){
            final[courseName]['syllabus'] = result['syllabus'];
        }
        else{
            final[courseName] = {'syllabus':result['syllabus']};
        }
    }
    return final;
}


//uploads data to an s3 bucket
function s3upload(bucketdir, filename, data){
    var key = filename;
    AWS.config.update({accessKeyId: config.s3AccessKeyId, secretAccessKey: config.s3SecretAccessKey});
    AWS.config.region = config.s3Region;
    var s3 = new AWS.S3({params: {Bucket: config.s3BucketName + bucketdir}});
    var params = {Key: key, ContentType: 'application/json', Body: JSON.stringify(data)};

    s3.upload(params, function(err, resp){
        if (err){
            console.log(err);
        }
    });
}
