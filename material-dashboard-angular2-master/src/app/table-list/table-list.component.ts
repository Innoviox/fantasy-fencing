import { Component, OnInit } from '@angular/core';
import { FencerService } from '.././fencer.service';


@Component({
  selector: 'app-table-list',
  templateUrl: './table-list.component.html',
  styleUrls: ['./table-list.component.css']
})
export class TableListComponent implements OnInit {
  constructor(private fencerService:FencerService) {  }
  someProperty:string = '';

  ngOnInit() {
    
    
    console.log(this.fencerService.cars);

    this.someProperty = this.fencerService.myData();
  }
}

