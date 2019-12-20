import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-table-list',
  templateUrl: './table-list.component.html',
  styleUrls: ['./table-list.component.css']
})
export class TableListComponent implements OnInit {

  constructor(
   // private appModule : AppModule 
) { }

ngOnInit(){
  //  this.appModule.getJSON().subscribe(data => {
  //       console.log(data);
  //   }); 
}

}
