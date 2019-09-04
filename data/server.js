let express = require('express')
let sqlite = require('sqlite3').verbose()

let app = express()

class DataServer {
    constructor(file) {
        this.music_data = new sqlite.Database(file)
        this.app = express()
    }
    
    
    start_server(port) {
        let db = new sqlite.Database('music_data.db')

        this.app.get('/playback', function(req, resp) {
            db.all('SELECT * FROM track_playback', function(err, row){
                return resp.json({data: row})
            })
        })

        this.app.get('/favorite', function(req, resp) {
            db.all('SELECT * FROM favorite_tracks', function(err, row) {
                return resp.json({data: row})
            })
        })

        this.app.get('/favorite', function(req, resp) {
            db.all('SELECT * FROM favorite_tracks', function(err, row) {
                return resp.json({data: row})
            })
        })

        this.app.listen(port)
    }
}

app = new DataServer('music_data.db')
app.start_server(3000)