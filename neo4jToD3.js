var neo4j = require('node-neo4j');
var fs = require('fs');
var personalsettings = require('../personalsettings.js');
var AWS = require('aws-sdk');

//Create a db object. We will using this object to work on the DB.
console.log(personalsettings.neo4jpassword);
db = new neo4j('http://neo4j:' + personalsettings.neo4jpassword + '@localhost:7474');


// queries the neo4j graph database and stores it in data.js in a d3 friendly format
uploadwholegraph();
uploadAllSubjects();
uploadAllCourses();

function uploadAllSubjects(){
    db.cypherQuery(
        'match (n:MITcourse) return distinct n.subject',{},
        function(err, result){
            if (err) {console.log(err);}
            var datalength = result.data.length;
            for (var i = 0; i < datalength; i++){
                var subject = result.data[i];
                console.log("uploading subject: " + subject);
                uploadSubject(subject);
            }
        }
    );
}

function uploadAllCourses(){
    db.cypherQuery(
        'match (n:MITcourse) return distinct n.name',{},
        function(err, result){
            if (err) {console.log(err);}
            var datalength = result.data.length;
            for (var i = 0; i < datalength; i++){
                var name = result.data[i];
                console.log("uploading course: " + name);
                uploadCourse(name);
            }
        }
    );
}


function uploadwholegraph(){
    console.log("uploading wholegraph");
    db.cypherQuery(
        'MATCH (n:MITcourse) RETURN n;',
        {}
        , function (err, result) {
            if (err) {
                //console.log(result);
                return console.log(err);
            }
            var noderes = result.data;
            db.cypherQuery(
                'MATCH (n:MITcourse) - [r] -> (m:MITcourse) RETURN id(n), id(m);',{},
                function (err, result) {
                    if (err) {
                        //console.log(result);
                        return console.log(err);
                    }
                    var data = parseLinks(noderes, result.data);
                    //console.log(data);
                    fs.writeFile("./js/data.js", "var data = " + JSON.stringify(data));
                    s3upload('vdorbslessons/Graphs', 'wholegraph',data);
                    return (data);
                }
            );
        }
    );
}

function uploadSubject(subject){
    db.cypherQuery(
        'MATCH (n:MITcourse {subject: \''+subject+'\'}) return distinct n;',{},
        function(err, result){
            if (err) {console.log(err);}
            var firstnodes = result.data;
            db.cypherQuery(
                 'match (m:MITcourse) - [:prereq*1..] -> (n:MITcourse {subject: \''+subject+'\'}) \
                  where not m.subject = \''+ subject + '\' return distinct m;',{},
                function(err, result){
                    if (err) {console.log(err);}
                    var allnodes = firstnodes.concat(result.data);
                    var namelist = [];
                    var uniquenodes = []
                    var i;
                    var numnodes = allnodes.length;
                    for (i = 0; i < numnodes; i++){
                        var name = allnodes[i].name;
                        if (namelist.indexOf(name) < 0){
                            uniquenodes.push(allnodes[i]);
                            namelist.push(name);
                        }
                    }
                    db.cypherQuery(
                          'match (m:MITcourse) - [:prereq] -> (n:MITcourse) \
                           where m.name in ' + JSON.stringify(namelist) + ' and \
                           n.name in ' + JSON.stringify(namelist) + ' return distinct id(m), id(n);',{},
                        function(err, result){
                            if (err) {console.log(err);}
                            var fin = parseLinks(uniquenodes, result.data);
                            s3upload('vdorbslessons/Graphs/Subjects', subject, fin);
                        }
                    );
                }
            );
        }
    );
}


function uploadCourse(course){
    db.cypherQuery(
        'MATCH (n:MITcourse {name: \''+course+'\'}) return distinct n;',{},
        function(err, result){
            if (err) {console.log(err);}
            var firstnodes = result.data;
            db.cypherQuery(
                'match (m:MITcourse) - [:prereq*1..] -> (n:MITcourse {name: \''+course+'\'}) \
                  where not m.name = \''+course+ '\' return distinct m;',{},
                function(err, result){
                    if (err) {console.log(err);}
                    var allnodes = firstnodes.concat(result.data);
                    var namelist = [];
                    var uniquenodes = []
                    var i;
                    var numnodes = allnodes.length;
                    for (i = 0; i < numnodes; i++){
                        var name = allnodes[i].name;
                        if (namelist.indexOf(name) < 0){
                            uniquenodes.push(allnodes[i]);
                            namelist.push(name);
                        }
                    }
                    db.cypherQuery(
                        'match (m:MITcourse) - [:prereq] -> (n:MITcourse) \
                         where m.name in ' + JSON.stringify(namelist) + ' and \
                           n.name in ' + JSON.stringify(namelist) + ' return distinct id(m), id(n);',{},
                        function(err, result){
                            if (err) {console.log(err);}
                            var fin = parseLinks(uniquenodes, result.data);
                            s3upload('vdorbslessons/Graphs/Courses', course, fin);
                        }
                    );
                }
            );
        }
    );
}

function parseNodesSubject(noderesp){
    var fin = [];
    var ar;
    var obj;
    for (var i = 0; i < noderesp.length; i++){
        ar = noderesp[i];
        for (var j = 0; j < ar.length; j++){
            obj = ar[j];
            fin.push(obj);
        }
    }
    console.log(fin);
    return fin;
}

// takes the nodes and links from the quries in the formatD3data function
// and outputs a d3 friendly json containing nodes and links.
function parseLinks(nodes,links){
    var map = {};
    for (var i = 0; i < nodes.length; i++){
        map[nodes[i]._id] = i;
    }
    var linkfin = [];
    for (var j = 0; j < links.length; j++){
        var temp = {};
        var source = links[j][0];
        var target = links[j][1];
        temp.source = map[source];
        temp.target = map[target];
        linkfin.push(temp);
    }
    var fin = {};
    fin.nodes = nodes;
    fin.links = linkfin;
    return fin;
}

//uploads data to an s3 bucket
function s3upload(bucketname, filename, data){
    var key = filename;
    AWS.config.update({accessKeyId: 'AKIAJFKCAKC5DOCNOZAQ', secretAccessKey: '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'});
    AWS.config.region = 'us-east-1';
    var s3 = new AWS.S3({params: {Bucket: bucketname}});
    var params = {Key: key, ContentType: 'application/json', Body: JSON.stringify(data)};

    s3.upload(params, function(err, resp){
        if (err){
            console.log(err);
        }
    });
}

