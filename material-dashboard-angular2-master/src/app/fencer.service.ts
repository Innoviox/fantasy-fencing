import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root'
})
export class FencerService{

 //stuff from guide
  cars = [
    'Ford','Chevrolet','Buick'
  ];
  myData(){
    return "example data";
  }


  //stuff for fencers
  // constructor(private http: Http) {
  //      var obj;
  //      this.getJSON().subscribe(data => obj=data, error => console.log(error));
  // }
  // public getJSON(): Observable<any> {
  //      return this.http.get("./file.json")
  //                      .map((res:any) => res.json())
  //                      .catch((error:any) => console.log(error));

  //  }
}

