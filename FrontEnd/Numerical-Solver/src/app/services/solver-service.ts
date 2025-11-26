import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RequestData } from '../models/request-data';
import { ResponseData } from '../models/response-data';

@Injectable({
  providedIn: 'root',
})
export class SolverService {
  private apiUrl = "http://localhost:5000"
  // private apiUrl = "https://4c951f5e866d2897bca6g1j3tghyyyyyb.oast.pro"

  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(
    private http: HttpClient
  ) {}


  getSolution(data : any) : Observable<ResponseData> {
    const url = this.apiUrl + "/solve"
    // const url = this.apiUrl
    return this.http.post<ResponseData>(url, data, this.httpOptions)
  }
}
