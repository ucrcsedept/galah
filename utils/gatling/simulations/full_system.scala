package galah

import com.excilys.ebi.gatling.core.Predef._
import com.excilys.ebi.gatling.http.Predef._
import com.excilys.ebi.gatling.jdbc.Predef._
import com.excilys.ebi.gatling.http.Headers.Names._
import akka.util.duration._
import bootstrap._

class FullSystem extends Simulation {

    def apply = {

        val nusers = Integer.getInteger("users", 150)
        val ramp_time = Integer.getInteger("ramp", 30).toLong
        val nqueries = Integer.getInteger("queries", 2)

        val httpConf = httpConfig
                .baseURL("http://localhost:5000")
                .acceptCharsetHeader("ISO-8859-1,utf-8;q=0.7,*;q=0.7")
                .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
                .acceptEncodingHeader("gzip, deflate")
                .acceptLanguageHeader("en-US,en;q=0.8")

        val upload_header = Map(
            "Content-Type" -> """multipart/form-data; boundary=---------------------------153842976519518901021827575179"""
        )

        val scn = scenario("average_student_galahlogin")
            .feed(csv("galah_users.csv"))
            .exec
                http("initial_contact")
                    .get("/")
            )
            .pause(2, 10)
            .exec(
                http("login")
                    .post("/login/")
                    .param("email", "${email}")
                    .param("password", "${password}")
                    .param("next", "")
                    .check(
                        regex(""".*<a href="/assignments/([0-9a-zA-Z]+)">.*""")
                        .saveAs("first_assignment")
                    )
            )
            .repeat(nqueries) {
                pause(2, 4)
                exec(
                    http("assignment")
                        .get("/assignments/${first_assignment}")
                )
                .pause(5, 20)
                .exec(
                    http("submit")
                        .post("/assignments/${first_assignment}/upload")
                        .headers(upload_header)
                            .fileBody("small_main.txt")
                        .check(
                            regex("""<a href="([0-9a-zA-Z]+)/download""")
                            .saveAs("my_submission")
                        )
                )
                .pause(4, 10)
                .exec(
                    http("redownload")
                        .get("/assignments/${first_assignment}/${my_submission}/download.tar.gz")
                )
                .pause(8, 20)
            }
            .exec(
                http("logout")
                    .get("/logout")
            )

        List(scn.configure.users(nusers).ramp(ramp_time).protocolConfig(httpConf))
    }
}
