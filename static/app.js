
const ROUTES = {"addData" : "/addData","deleteData":"/deleteData","updateData":"/updateData"}
const GET = "GET"
const POST = "POST"


async function sendRequest(route,data,methodType)
{
    console.log(route+" "+data+" "+methodType)
    let res =  false;
    let out = await fetch(route,{
        method: methodType,
        headers:{'Content-Type': 'application/json'},
        body: JSON.stringify(data)}).then(
            response => {
                return response.json()
                }).then(data => {
                    if (data.status === "failed")
                    {
                        alert("Operation Failed! \n 1. Check if there is any product/category/unit with the same name \n 2. Check if selected quantity is in Stock  \n\nIf problem still persists Contact Support")
                    }
                    else
                    {
                        res = true;
                    }
                }).catch(error =>{
                    console.log(error + " Error updating the data, Contact Support")
        });
    return res
}

function saveData()
{
      data = {}
      const tabContents = document.querySelectorAll('#Contents .tab-pane');
      let activeTab;
      for (const tab of tabContents)
      {
        if (tab.classList.contains('active'))
        {
            activeTab = tab.id;
            break;
        }
      }
      if (activeTab === 'item')
      {
         data.type = "product"
         const itemName =  document.getElementById('itemName').value;
         const unit =  document.getElementById('units').value;
         const category =  document.getElementById('categories').value;
         const rate =  document.getElementById('rate').value;
         const quantity =  document.getElementById('quantity').value;
         if((!itemName || !unit || !category || !rate || !quantity))
         {
              alert("Kindly fill all feilds !!")
              return
         }
         else if(isNaN(rate) || isNaN(quantity) )
         {
               alert(" rate / quantity should be a number !!")
               return
         }
         else
         {
            data.itemName = itemName
            data.unit = unit
            data.category = category
            data.rate = rate
            data.quantity = quantity
         }
      }
      else if (activeTab === 'category')
      {
            data.type = "category"
            const categoryName = document.getElementById('categoryName').value;
            if(!categoryName)
            {
                  alert("Kindly fill all feilds !!")
                  return
            }
            else
            {
                data.categoryName = categoryName
            }
       }
       else if (activeTab === 'unit')
       {
            data.type = "unit"
            const unitName = document.getElementById('unitName').value;
            if(!unitName)
            {
                  alert("Kindly fill all feilds !!")
                  return
            }
            else
            {
                data.unitName = unitName
            }
       }
       res = sendRequest(ROUTES.addData,data,POST)
       window.location.reload();

}


 function fillEditModal(id, name, category, unit, price,quantity)
 {
    document.getElementById('editQuantity').value = quantity;
    document.getElementById('editName').value = name;
    document.getElementById('editCategory').value = category;
    document.getElementById('editUnit').value = unit;
    document.getElementById('editPrice').value = price;
    document.getElementById('editItemId').value = id;
}

function fillCatEditModal(id,name)
{
    document.getElementById('editName').value = name;
    document.getElementById('editItemId').value = id;
}

function deleteProduct(type,id)
{
    if (confirm("Are you sure, You want to delete ? \n (Note : If you're deleting a category / unit it will delete all products using that category / unit )"))
    {
        let data = {}
        data.type = type
        data.id = id
        res = sendRequest(ROUTES.deleteData,data,POST)
        window.location.reload();
    }

}

function updateProduct()
{
    let data = {};
    data.type = "item"
    data.id = document.getElementById('editItemId').value;
    data.name = document.getElementById('editName').value;
    data.price = document.getElementById('editPrice').value;
    data.unit = document.getElementById('editUnit').value;
    data.category = document.getElementById('editCategory').value;
    data.quantity = document.getElementById('editQuantity').value;
    res = sendRequest(ROUTES.updateData,data,POST);
    window.location.reload();
}

function updateCategory(type)
{
    let data = {};
    data.type = type
    data.id = document.getElementById('editItemId').value;
    data.name = document.getElementById('editName').value;
    res = sendRequest(ROUTES.updateData,data,POST);
    window.location.reload();
}


function applyFilters(username,type)
{
      data = {}
      const tabContents = document.querySelectorAll('#filterTabContent .tab-pane');
      let activeTab;
      for (const tab of tabContents)
      {
        if (tab.classList.contains('active'))
        {
            activeTab = tab.id;
            break;
        }
      }
      data.sortType = activeTab;
      if (activeTab === 'category')
      {
        const categorySelect = document.getElementById("categorySelect");
        const selectedCategory = categorySelect.value;
        data.value = selectedCategory
      }
      else if (activeTab === 'price')
      {
          const lowToHigh = document.getElementById("lowToHigh");
          const highToLow = document.getElementById("highToLow");
          let selectedPriceSort = null;
          if (lowToHigh.checked)
          {
            selectedPriceSort = "lowToHigh";
          }
          else if (highToLow.checked)
          {
            selectedPriceSort = "highToLow";
          }
          data.value = selectedPriceSort
      }
      else if (activeTab === 'unit')
      {
          const unitSelect = document.getElementById("unitSelect");
          const selectedUnit = unitSelect.value;
          data.value = selectedUnit
      }
       if(type === "1")
       {
            window.location.href = '/user/'+username+'/products?sortType='+data.sortType+'&value='+data.value
       }
       else
       {
            window.location.href = '/user/'+username+'?sortType='+data.sortType+'&value='+data.value
       }

}

function fillCartAdder(id, price,qnty)
{
    document.getElementById("cartItemId").value = id
    document.getElementById("pricePerItem").value = price
    document.getElementById("editQnty").value = 0
    document.getElementById("TotalPrice").value = 0
    document.getElementById("editQnty").max = qnty
}


function addToCart()
{
    let data = {}
    data.type = "cart"
    data.id = document.getElementById("cartItemId").value
    data.quantity = document.getElementById("editQnty").value
    if(parseInt(data.quantity) >= 1 )
    {
        res = sendRequest(ROUTES.addData,data,POST)
        if(res)
        {
             alert(" Succefully added to the cart !")
             window.location.reload();
        }
    }
    else
    {
        alert(" You Should atleast add one item in the cart ")
    }
}


function deleteFromCart(cartId,itemId)
{
    let data = {}
    data.type= 'cart'
    data.cartId = cartId
    data.itemId = itemId
    res = sendRequest(ROUTES.deleteData,data,POST)
    window.location.reload();
}

function checkOut()
{
    data = {}
    data.type = "checkOut"
    res = sendRequest(ROUTES.updateData,data,POST)
    alert(" Order placed Successfully ")
    window.location.reload();
}
