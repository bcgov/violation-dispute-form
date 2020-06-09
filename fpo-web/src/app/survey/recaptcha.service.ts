import { Injectable } from '@angular/core';
import {HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs';

@Injectable()
export class RecaptchaService {

  constructor(private http: HttpClient) { }

 sendToken(token){
    return console.log("success");
    //return this.http.post<any>("/token_validate", {recaptcha: token})
}

}
