/*probability.js
  12-25-2008
  JavaScript
  Copyright (C)2008 Steven Whitney.
  Initially published by http://25yearsofprogramming.com.

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License (GPL)
  Version 3 as published by the Free Software Foundation.
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Functions related to probability calculations.

*/
//----------------------------------------------------------------------------------------------
// Calculates a point Z(x), the Probability Density Function, on any normal curve. 
// This is the height of the point ON the normal curve.
// For values on the Standard Normal Curve, call with Mean = 0, StdDev = 1.
function NormalDensityZx(x, Mean, StdDev)
{
    var a = x - Mean;
    return Math.exp(-(a * a) / (2 * StdDev * StdDev)) / (Math.sqrt(2 * Math.PI) * StdDev); 
}
//----------------------------------------------------------------------------------------------
// Calculates Q(x), the right tail area under the Standard Normal Curve. 
function StandardNormalQx(x)
{
    if(x === 0)// no approximation necessary for 0
	return 0.50;
    
    var t1,t2,t3,t4,t5,qx;
    var negative = false;
    if(x < 0)
	{
	    x = -x;
	    negative = true;
	    }
    t1 = 1 / (1 + (0.2316419 * x)); 
    t2 = t1 * t1; 
    t3 = t2 * t1; 
    t4 = t3 * t1; 
    t5 = t4 * t1;
    qx = NormalDensityZx(x,0,1) * ((0.319381530 * t1) + (-0.356563782 * t2) + 
				   (1.781477937 * t3) + (-1.821255978 * t4) + (1.330274429 * t5));
    if(negative == true)
	qx = 1 - qx;
    return qx;
}
//------------------------------------------------------------------------------
// Calculates P(x), the left tail area under the Standard Normal Curve,
// which is 1 - Q(x). 
function StandardNormalPx(x)
{
    return 1 - StandardNormalQx(x);
}
//------------------------------------------------------------------------------
// Calculates A(x), the area under the Standard Normal Curve between +x and -x. 
function StandardNormalAx(x)
{
    return 1 - (2 * StandardNormalQx(Math.abs(x)));
}
//------------------------------------------------------------------------------
